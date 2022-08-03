from curses import KEY_ENTER
import pygame
from sys import exit
from random import randint


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = player_surf.get_rect(center = (400, 530))
        self.curr_health = 1000
        self.max_health = 1000
        self.health_bar_length = 64
        self.health_ratio = self.max_health / self.health_bar_length

    def draw(self):
        screen.blit(player_surf, self.rect)
        self.draw_health_bar()

    def move(self, diff):
        if self.rect.x + diff > 0 and self.rect.x + diff < 800 - self.rect.width:
            self.rect.x += diff

    def shoot_laser(self):
        bullet = Bullet(game.player.rect.x + game.player.rect.width // 2)
        bullet_group.add(bullet)
        laser_sound.play()

    def draw_health_bar(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y + self.rect.height + 5, self.max_health / self.health_ratio, 20))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y + self.rect.height + 5, self.curr_health / self.health_ratio, 20))
        pygame.draw.rect(screen, (255, 255, 255), (self.rect.x, self.rect.y + self.rect.height + 5, self.max_health / self.health_ratio, 20), 1)
        

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = bullet_surf
        self.rect = self.image.get_rect(center = (pos, 480))

    def update(self):
        self.rect.y -= 15

        if self.rect.y < -self.rect.height:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, type, pos):
        super().__init__()
        self.type = type
        
        if type == 0:
            self.image = alien_surf1
            self.damage = 50
        elif type == 1:
            self.image = alien_surf2
            self.damage = 100
        else:
            self.image = alien_surf3
            self.damage = 150

        self.rect = self.image.get_rect(midbottom = (pos, 0))
        
    def update(self):
        self.rect.y += 2

        if self.rect.y > 600:
            self.kill

    def shoot_laser(self):
        if self.type == 0:
                x = self.rect.x + self.rect.width // 2
                y = self.rect.y + self.rect.height
                bullet = AlienBullet(1, x, y, 50)
                alien_bullet_group.add(bullet)
        elif self.type == 1:
            x = self.rect.x
            y = self.rect.y + self.rect.height
            bullet = AlienBullet(1, x, y, 100)
            alien_bullet_group.add(bullet)

            x = self.rect.x + self.rect.width
            y = self.rect.y + self.rect.height
            bullet = AlienBullet(1, x, y, 100)
            alien_bullet_group.add(bullet)
        else:
            x = self.rect.x + self.rect.width // 2
            y = self.rect.y + self.rect.height
            bullet = AlienBullet(1, x, y, 150)
            alien_bullet_group.add(bullet)

            x = self.rect.x
            y = self.rect.y + self.rect.height
            bullet = AlienBullet(0, x, y, 150)
            alien_bullet_group.add(bullet)

            x = self.rect.x + self.rect.width
            y = self.rect.y + self.rect.height
            bullet = AlienBullet(2, x, y, 150)
            alien_bullet_group.add(bullet)


class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, type, x, y, damage):
        super().__init__()
        self.type = type
        self.damage = damage

        if type == 0:
            self.image = pygame.transform.rotate(alien_bullet_surf, -45)
        elif type == 1:
            self.image = alien_bullet_surf
        else:
            self.image = pygame.transform.rotate(alien_bullet_surf, 45)

        self.rect = self.image.get_rect(midtop = (x, y))

    def update(self):
        if self.type == 0:
            self.rect.x -= 2
            self.rect.y += 4

            if self.rect.x <= -self.rect.width or self.rect.y >= 600:
                self.kill()
        elif self.type == 1:
            self.rect.y += 4

            if self.rect.y >= 600:
                self.kill()
        else:
            self.rect.x += 2
            self.rect.y += 4

            if self.rect.x >= 800 or self.rect.y >= 600:
                self.kill()


class Health(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = health_surf
        self.rect = self.image.get_rect(midbottom = (pos, 0))
        
    def update(self):
        self.rect.y += 2

        if self.rect.y > 600:
            self.kill


class Game:
    def __init__(self):
        super().__init__()
        self.high_score = 0
        self.reset()

    def reset(self):
        self.player = Player()
        player_group.add(self.player)
        self.diff = 0
        self.score = 0
        self.interval = 3000
        self.is_active = True

    def spawn_aliens(self):
        pos = randint(32, 568)
        alien_type = randint(0, 2)
        alien = Alien(alien_type, pos)
        alien_group.add(alien)
        self.interval -= 50

        if self.interval <= 1000:
            self.interval = 1000

        pygame.time.set_timer(SPAWN_ALIENS, self.interval)

    def spawn_alien_bullets(self):
        for alien in alien_group:
            alien.shoot_laser()

    def spawn_health(self):
        pos = randint(32, 568)
        health = Health(pos)
        health_group.add(health)

    def alien_bullet_collision(self):
        collisions = pygame.sprite.groupcollide(alien_group, bullet_group, True, True)

        if collisions:
            for alien in collisions:
                self.score += alien.type + 1
                explosion_sound.play()

    def player_alien_collision(self):
        collisions = pygame.sprite.spritecollide(player_group.sprite, alien_bullet_group, True)

        if collisions:
            for bullet in collisions:
                self.player.curr_health -= bullet.damage
                hit_sound.play()

                if self.player.curr_health <= 0:
                    if self.high_score < self.score:
                        self.high_score = self.score
                    
                    self.is_active = False

    def player_bullet_collision(self):
        collisions = pygame.sprite.spritecollide(player_group.sprite, alien_group, True)

        if collisions:
            for alien in collisions:
                self.player.curr_health -= alien.damage
                hit_sound.play()

                if self.player.curr_health <= 0:
                    if self.high_score < self.score:
                        self.high_score = self.score
                    
                    self.is_active = False

    def player_health_collide(self):
        if pygame.sprite.spritecollide(player_group.sprite, health_group, True) and self.player.curr_health:
            self.player.curr_health += 200
            health_recovery_sound.play()

            if self.player.curr_health > self.player.max_health:
                self.player.curr_health = self.player.max_health

    def draw_player(self):
        self.player.draw()

    def draw_bullets(self):
        bullet_group.draw(screen)
        bullet_group.update()
        
    def draw_aliens(self):
        alien_group.draw(screen)
        alien_group.update()

    def draw_alien_bullets(self):
        alien_bullet_group.draw(screen)
        alien_bullet_group.update()

    def draw_health(self):
        health_group.draw(screen)
        health_group.update()

    def draw_score(self):
        if self.is_active:
            score_text = 'Score: ' + str(self.score)
            score_surf = score_font.render(score_text, True, (255, 215, 0))
            score_rect = score_surf.get_rect(topleft = (5, 5))
            screen.blit(score_surf, score_rect)
        else:
            score_text = 'Score: ' + str(self.score)
            score_surf = score_font.render(score_text, True, (255, 215, 0))
            score_rect = score_surf.get_rect(center = (400, 200))
            screen.blit(score_surf, score_rect)

            high_score_text = 'High score: ' + str(self.high_score)
            high_score_surf = score_font.render(high_score_text, True, (255, 215, 0))
            high_score_rect = high_score_surf.get_rect(center = (400, 250))
            screen.blit(high_score_surf, high_score_rect)

            message_text = 'Press space for new game'
            message_surf = score_font.render(message_text, True, (255, 215, 0))
            message_rect = message_surf.get_rect(center = (400, 300))
            screen.blit(message_surf, message_rect)


pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Space Invaders')
clock = pygame.time.Clock()
icon = pygame.image.load('images/player.png')
pygame.display.set_icon(icon)

bg_surf = pygame.image.load('images/background.png')
player_surf = pygame.image.load('images/player.png')
bullet_surf = pygame.image.load('images/bullet.png')
alien_surf1 = pygame.image.load('images/alien1.png')
alien_surf2 = pygame.image.load('images/alien2.png')
alien_surf3 = pygame.image.load('images/alien3.png')
alien_bullet_surf = pygame.image.load('images/alien_bullet.png')
alien_bullet_surf = pygame.transform.rotate(alien_bullet_surf, 180)
health_surf = pygame.image.load('images/health.png')
score_font = pygame.font.Font('fonts/04B_19.TTF', 45)

laser_sound = pygame.mixer.Sound('sounds/laser.wav')
explosion_sound = pygame.mixer.Sound('sounds/explosion.wav')
health_recovery_sound = pygame.mixer.Sound('sounds/health_recovery.wav')
hit_sound = pygame.mixer.Sound('sounds/hit.wav')
bg_music = pygame.mixer.Sound('sounds/background.wav')
bg_music.play(loops=-1)

player_group = pygame.sprite.GroupSingle()
alien_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
health_group = pygame.sprite.Group()

SPAWN_ALIENS = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ALIENS, 3000)
SPAWN_ALIEN_BULLETS = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ALIEN_BULLETS, 1500)
SPAWN_HEALTH = pygame.USEREVENT + 3
pygame.time.set_timer(SPAWN_HEALTH, 5000)
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == SPAWN_ALIENS:
            game.spawn_aliens()

        if event.type == SPAWN_ALIEN_BULLETS:
            game.spawn_alien_bullets()

        if event.type == SPAWN_HEALTH:
            game.spawn_health()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.is_active:
                    game.player.shoot_laser()
                else:
                    alien_group.empty()
                    alien_bullet_group.empty()
                    bullet_group.empty()
                    health_group.empty()
                    pygame.time.set_timer(SPAWN_ALIENS, 1500)
                    game.player.kill()
                    game.reset()
            
            if event.key == pygame.K_LEFT:
                game.diff = -5
            elif event.key == pygame.K_RIGHT:
                game.diff = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                game.diff = 0

    screen.blit(bg_surf, (0, 0))

    if game.is_active:
        game.player.move(game.diff)
        game.draw_bullets()
        game.alien_bullet_collision()
        game.player_alien_collision()
        game.player_bullet_collision()
        game.player_health_collide()
    
    game.draw_player()
    game.draw_aliens()
    game.draw_alien_bullets()
    game.draw_health()
    game.draw_score()

    pygame.display.update()
    clock.tick(60)
    