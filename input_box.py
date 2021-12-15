import pygame

COLOR_INACTIVE = pygame.Color('grey')
COLOR_ACTIVE = pygame.Color('black')



class InputBox:

    def __init__(self, x, y, w, h,FONT, content='' , number_only=True , size_limit=3 , numeric_limit=500 ):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.content = content
        self.final_content = ""
        self.FONT = FONT
        self.txt_surface = FONT.render(content, True, self.color)
        self.active = False
        self.number_only = number_only
        self.size_limit = size_limit
        self.numeric_limit = numeric_limit

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.final_content = self.content
                    self.content = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.content = self.content[:-1]
                else:
                    if len(self.content) < self.size_limit:
                        if self.number_only:
                            if event.unicode.isnumeric():
                                if int(event.unicode) < self.numeric_limit:
                                    self.content += event.unicode
                        else:
                           self.content += event.unicode
                # Re-render the content.
                self.txt_surface = self.FONT.render(self.content, True, self.color)

    def update(self):
        # Resize the box if the content is too long.
        width = max(self.rect.w, self.txt_surface.get_width()+10)
        self.rect.w = width

    def set_final_content(self , new_final_content):
        self.final_content = new_final_content
    def set_active(self , new_active):
        self.active = new_active

    def draw(self, screen):
        # Blit the content.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.

        pygame.draw.rect(screen, self.color, self.rect, 2)
