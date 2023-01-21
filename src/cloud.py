import jax
import jax.numpy as jnp

class Cloud(object):
    def __init__(self, Nx=10, Ny=10):
        self.Nx = Nx
        self.Ny = Ny
        self.N = self.Nx*self.Ny

        self.make_global_indices()

        self.make_node_coordinates()

        self.make_boundaries()

        self.make_local_supports()


    def make_node_coordinates(self):
        x = jnp.linspace(0, 1., self.Nx)
        y = jnp.linspace(0, 1., self.Ny)
        xx, yy = jnp.meshgrid(x, y)

        self.nodes = jnp.zeros((self.N, 2), dtype=jnp.float32)

        for i in range(self.Nx):
            for j in range(self.Ny):
                global_id = self.global_indices[i,j]
                self.nodes = self.nodes.at[global_id].set(jnp.array([xx[j,i], yy[j,i]]))

    def make_global_indices(self):
        ## defines the 2d to 1d indices and vice-versa

        self.global_indices = jnp.zeros((self.Nx, self.Ny), dtype=jnp.int32)
        self.global_indices_rev = jnp.zeros((self.N, 2), dtype=jnp.int32)

        count = 0
        for i in range(self.Nx):
            for j in range(self.Ny):
                self.global_indices = self.global_indices.at[i,j].set(count)
                self.global_indices_rev = self.global_indices_rev.at[count].set(jnp.array([i,j]))
                count += 1


    def make_boundaries(self):
        bds = jnp.zeros((self.Nx, self.Ny), dtype=jnp.int32)
        ## internal: 0
        ## dirichlet: 1
        ## neumann: 2
        ## external: -1

        bds = jnp.zeros((self.N), dtype=jnp.int32)
        for i in range(self.N):
            [k, l] = list(self.global_indices_rev[i])
            if k == 0 or l == 0 or l == self.Ny-1:
                bds = bds.at[i].set(1)
            elif k == self.Nx-1:
                bds = bds.at[i].set(2)

        self.M = jnp.size(bds[bds==0])
        self.MD = jnp.size(bds[bds==1])
        self.MN = jnp.size(bds[bds==2])
        self.boundaries = bds

    def distance(self, node1, node2):
        return jnp.linalg.norm(node1 - node2)**2


    def make_local_supports(self):
        ## finds the 7 nearest neighbords of each node
        self.local_supports = jnp.zeros((self.N, 7), dtype=jnp.int32)

        for i in range(self.N):
            distances = jnp.zeros((self.N), dtype=jnp.float32)
            for j in range(self.N):
                    distances = distances.at[j].set(self.distance(self.nodes[i], self.nodes[j]))

            closest_neighbours = jnp.argsort(distances)
            self.local_supports = self.local_supports.at[i].set(closest_neighbours[1:8])      ## node i is closest to itself

if __name__ == '__main__':
    cloud = Cloud(Nx=7, Ny=5)
    print("\n=== Meshfree cloud for RBF-FD method ===\n")
    print()
    print("Cloud bounding box: Nx =", cloud.Nx, " -  Ny =", cloud.Ny)
    print()
    print("Global indices:\n", cloud.global_indices)
    # print(cloud.global_indices_rev)
    print()
    print("Boundary types - 0=internal, 1=dirichlet, 2=neumann:\n", cloud.boundaries)
    print("Number of: \n\t-Internal points: M =", cloud.M, "\n\t-Dirichlet points: MD =", cloud.MD, "\n\t-Neumann points: MN =", cloud.MN)
    print()
    print("Node coordinates:\n", cloud.nodes)
    print()
    print("Local supports (7 closest neighbours):\n", cloud.local_supports)
    