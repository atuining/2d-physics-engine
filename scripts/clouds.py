import random
import numpy as np


class Cloud:

    def __init__(self, pos, img, speed, depth):
        self.pos = np.array(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed

    def render(self, surf, offset=np.array((0., 0.))):
        render_pos = self.pos - offset * self.depth

        print(render_pos)
        print(surf.get_size())
        print(self.img.get_size())
        surf.blit(
            self.img, render_pos %
            (np.array(surf.get_size()) + np.array(self.img.get_size())) -
            np.array(self.img.get_size()))

        # modulo here to loop the image back around when it goes off screen
        # add img width to modulo so there is a buffer before it loops
        # - self.img.get_width() and - self.img.get_height() are to wrap image around edge of screen


class Clouds:

    def __init__(self, cloud_images, count=16):
        self.clouds = []

        for i in range(count):
            self.clouds.append(
                Cloud(pos=(random.random() * 99999, random.random() * 99999),
                      img=random.choice(cloud_images),
                      speed=random.random() * 0.05 + 0.05,
                      depth=random.random() * 0.6 + 0.2))

        self.clouds.sort(key=lambda x: x.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(surf, offset)
