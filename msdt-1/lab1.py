'''
В данном проекте представлена часть моего pet-проекта
по вычислению оптимальной стратегии в игре Buckshoot Roulette
(часть потому что оригинальный код написан на C#, а переписывать все лень.
Несмотря на это оригинальный вариант я вставил без правок по стилям)
Оригинал: https://github.com/Daytel/Roulette
'''

# Класс вычисления наилучшей стратегии
class Solution:

    # Сбор результатов
    '''
    self - решение, max_hp - начальное hp игроков в раунде
    '''

    def __init__( self, max_hp ):

        # Путь выборов
        self.choices = [] 

        # Численные коеффициенты: Effective Values, wins, loses
        self.EV = []
        self.wins = []
        self.loses = []
        
        # Максимум здоровья
        self.max_hp = max_hp 

    '''
    self - решение, game_params - игровые показатели
    '''

    # Задача 1. Добавить расклад для боевые + холостые
    def me_calculate( self, game_params ):
        
        '''
        Игровые показатели:
        YHP - здоровье игрока, DHP - здоровье дилера, LR - боевые патроны, BL - холостые патроны,
        CH - вероятность события, PATH - путь действий, MI - предметы игрока, HI - предметы дилера,
        FM - первый ход
        '''
        if self == None or len(game_params) != 9:
            return

        YHP = game_params[0]
        DHP = game_params[1]
        LR = game_params[2]
        BL = game_params[3]
        ch = game_params[4]
        path = game_params[5]
        MI = game_params[6]
        HI = game_params[7]
        FM = game_params.FM[8]

        # Условия завершения рекурсии
        # 1. Кто-то умер
        if YHP < 1:
            self.loses[ self.choices.index(path) ] += ch
        elif DHP < 1:
            self.wins[ self.choices.index(path) ] += ch
        
        # 2. Кончились патроны
        elif LR + BL != 0:
            
            # Иначе считаем стратегию
            # Если первый ход - создаём новую ветвь
            if FM and path == "":
                self.choices.append(path)
                self.EV.append(0)
                self.wins.append(0)
                self.loses.append(0)

            # 1. Процесс хила

            # Использование "Лекарства" экстренно
            if MI["Cigarettes"] == 0 and ( MI["Adrenalin"] == 0 and HI["Cigarettes"] == 0 and
                                           Simulation.kill_me( [ YHP, LR, BL, MI, HI ] ) > 0.5 and
                                           Simulation.can_kill( [ DHP, LR , BL, MI, HI ] ) < 0.5
                                         ):
                
                # Нам выгодно есть таблетку
                if FM:
                    self.choices[-1] += "Medicine "
                    path += "Medicine "
                MI["Medicine"] -= 1
                self.me_calculate( self, [ YHP + 2, DHP, LR, BL, ch * 0.5, path, MI, HI, FM] )
                self.me_calculate( self, [ YHP - 1, DHP, LR, BL, ch * 0.5, path, MI, HI, FM ] )

            # Обычное использование сигарет и таблеток
            if YHP != self.max_hp:

                # Таблетки
                if MI["Medicine"] != 0 and YHP == 2 and self.max_hp == 4:
                    if FM:
                        self.choices[-1] += "Medicine "
                        path += "Medicine "
                    MI["Medicine"] -= 1
                    self.me_calculate( self, [ YHP + 2, DHP, LR, BL, ch * 0.5, path, MI, HI, FM ] )
                    self.me_calculate( self, [ YHP - 1, DHP, LR, BL, ch * 0.5, path, MI, HI, FM ] )
                
                # Сигареты
                elif MI["Cigarettes"] != 0:
                    if FM:
                        self.choices[-1] += "Cigarettes "
                        path += "Cigarettes "
                    MI["Cigarettes"] -= 1
                    self.me_calculate( self, [ YHP + 1, DHP, LR, BL, ch, path, MI, HI, FM ] )

            # Использование патронов
            # Остались холостые
            if LR == 0:
                
                # Проверка на условие 100% победы
                if DHP == 1:
                    if MI["Inverter"] != 0 or ( MI["Adrenalin"] != 0 and HI["Inverter"] != 0 ):
                        if FM:
                            self.choices[-1] += "Inverter Dealer"
                            path += "Inverter Dealer"
                        self.EV[-1] += ch
                        self.dealer_calculate( self, [ YHP, DHP - 1, LR, BL - 1, ch, path, MI, HI, False ] )
                    else:
                        if FM:
                            self.choices[-1] += "Me"
                            path += "Me"
                        self.me_calculate( self [ YHP, DHP, LR, 0, ch, path, MI, HI, FM ] )

                elif DHP == 2:

                    # Наручники + 2 Инвертора
                    if BL >= 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and
                                     MI["Inverter"] + min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Saw"] ) ) > 1
                                   ):
                        if FM:
                            self.choices[-1] += "Handcuffs Inverter Dealer Inverter Dealer"
                            path += "Handcuffs Inverter Dealer Inverter Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR, BL - 2, ch, path, MI, HI, False ] )
                    
                    # Пила + Инвертор
                    elif MI["Saw"] + min( MI["Adrenalin"], HI["Saw"] ) != 0 and MI["Inverter"] + \
                                          min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Saw"] ), HI["Inverter"]
                                        ) != 0:
                        if FM:
                            self.choices[-1] += "Inverter Saw Dealer"
                            path += "Inverter Saw Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR, BL - 2, ch, path, MI, HI, False ] )

                    # На последний патрон Инвертор
                    elif BL == 1 and ( MI["Inverter"] != 0 or ( MI["Adrenalin"] != 0 and HI["Adrenalin"] != 0 ) ):
                        if FM:
                            self.choices[-1] += "Inverter Dealer"
                            path += "Inverter Dealer"
                        self.EV[-1] += ch
                        self.dealer_calculate( self, [ YHP, DHP - 1, LR, 0, ch, path, MI, HI, False ] )

                    else:
                        if FM:
                            self.choices[-1] += "Me "
                            path += "Me "
                        self.me_calculate( self, [ YHP, DHP, LR, BL - 1, ch, path, MI, HI, FM ] )
                
                elif DHP == 3:

                    # Наручники + Пила + 2 Инвертора
                    if BL >=2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and MI["Saw"] +
                                    min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Handcuffs"]), HI["Saw"] ) != 0 and
                                    MI["Inverter"] + \
                                    min( MI["Adrenalin"] - Simulation.use_adrenalin( 2, MI["Handcuffs"] + MI["Saw"] ), HI["Inverter"] ) > 1
                                  ):
                        if (FM):
                            self.choices[-1] += "Handcuffs Inverter Saw Dealer Inverter Dealer"
                            path += "Handcuffs Inverter Saw Dealer Inverter Dealer"
                        self.EV[-1] += ch * 3
                        self.dealer_calculate( self, [ YHP, DHP - 3, LR, BL - 2, ch, path, MI, HI, False ] )
                    
                    # На 2 патрона Наручники + 2 инвертора
                    elif BL == 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and
                                       MI["Inverter"] +
                                       min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Saw"] ), HI["Inverter"] ) > 1
                                     ):
                        if FM:
                            self.choices[-1] += "Handcuffs Inverter Dealer Inverter Dealer"
                            path += "Handcuffs Inverter Dealer Inverter Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR, 0, ch, path, MI, HI, False ] )

                    # На последний патрон Пила + Инвертор
                    elif BL == 1 and ( MI["Saw"] + min( MI["Adrenalin"], HI["Saw"] ) != 0 and MI["Inverter"] + \
                                       min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Saw"]), HI["Inverter"] ) != 0
                                     ):
                        if FM:
                            self.choices[-1] += "Inverter Saw Dealer"
                            path += "Inverter Saw Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR, 0, ch, path, MI, HI, False ] )

                    # На последний Инвертор
                    elif BL == 1 and ( MI["Inverter"] != 0 or ( MI["Adrenalin"] != 0 and HI["Inverter"] != 0 ) ):
                        if FM:
                            self.choices[-1] += "Inverter Dealer"
                            path += "Inverter Dealer"
                        self.EV[-1] += ch
                        self.dealer_calculate( self, [ YHP, DHP - 1, LR, 0, ch, path, MI, HI, False ] )

                    else:
                        if FM:
                            self.choices[-1] += "Me... "
                            path += "Me... "
                        self.me_calculate( self, [ YHP, DHP, LR, BL - 1, ch, path, MI, HI, FM ] )

                # DHP == 4
                else:  

                    # Наручники + 2 Пилы + 2 Инвертора
                    if BL >= 2 and ( MI["Handcuffs"] + min(MI["Adrenalin"], HI["Handcuffs"]) != 0 and MI["Saw"] + \
                                     min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Handcuffs"] ), HI["Saw"] ) > 1 and
                                     MI["Inverter"] + \
                                     min( MI["Adrenalin"] - Simulation.use_adrenalin( 3, MI["Handcuffs"] + MI["Saw"] ), HI["Inverter"] ) > 1
                                   ):
                        if FM:
                            self.choices[-1] += "Handcuffs Inverter Saw Dealer Inverter Saw Dealer"
                            path += "Handcuffs Inverter Saw Dealer Inverter Saw Dealer"
                        self.EV[-1] += ch * 4
                        self.dealer_calculate( self, [ YHP, DHP - 4, LR, 0, ch, path, MI, HI, False ] )
                    
                    # На 2 патрона Наручники + Пила + 2 Инвертора
                    elif BL == 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and
                                       MI["Saw"] + min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Handcuffs"]), HI["Saw"] ) != 0 and
                                       MI["Inverter"] + min( MI["Adrenalin"] - Simulation.use_adrenalin( 2, MI["Handcuffs"] + MI["Saw"] ), HI["Inverter"] ) > 1
                                     ):
                        if FM:
                            self.choices[-1] += "Handcuffs Inverter Saw Dealer Inverter Dealer"
                            path += "Handcuffs Inverter Saw Dealer Inverter Dealer"
                        self.EV[-1] += ch * 3
                        self.dealer_calculate( self, [ YHP, DHP - 3, LR, 0, ch, path, MI, HI, False ] )
                    
                    # На 2 патрона Наручники + 2 инвертора
                    elif BL == 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and MI["Inverter"] + \
                                       min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Saw"] ), HI["Inverter"] ) > 1
                                     ):
                        if FM:
                            self.choices[-1] += "Handcuffs Inverter Dealer Inverter Dealer"
                            path += "Handcuffs Inverter Dealer Inverter Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR, 0, ch, path, MI, HI, False ] )

                    # На последний патрон Пила + Инвертор
                    elif BL == 1 and ( MI["Saw"] + min( MI["Adrenalin"], HI["Saw"] ) != 0 and MI["Inverter"] +\
                                       min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Saw"] ), HI["Inverter"] ) != 0
                                     ):
                        if FM:
                            self.choices[-1] += "Inverter Saw Dealer"
                            path += "Inverter Saw Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR, 0, ch, path, MI, HI, False ] )
                    
                    # На последний Инвертор
                    elif BL == 1 and ( MI["Inverter"] != 0 or ( MI["Adrenalin"] != 0 and HI["Inverter"] != 0 ) ):
                        if FM:
                            self.choices[-1] += "Inverter Dealer"
                            path += "Inverter Dealer"
                        self.EV[-1] += ch
                        self.dealer_calculate( self, [ YHP, DHP - 1, LR, 0, ch, path, MI, HI, False ] )

                    else:
                        if FM:
                            self.choises[-1] += "Me "
                            path += "Me "
                        self.me_calculate( self, [ YHP, DHP, LR, BL - 1, ch, path, MI, HI, FM ] )

            elif BL == 0: # Остались боевые
                
                # Проверка на условие 100% победы
                if DHP == 1:
                    if FM:
                        self.choices[-1] += "Dealer"
                        path += "Dealer"
                    self.EV[-1] += ch
                    self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )

                elif DHP == 2:

                    # 2 патрона + Наручники
                    if LR >= 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 ):
                        if FM:
                            self.choices[-1] += "Handcuffs Dealer Dealer"
                            path += "Handcuffs Dealer Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR - 2, BL, ch, path, MI, HI, False ] )
                    
                    # Пила
                    elif MI["Saw"] + min( MI["Adrenalin"], HI["Saw"] ) != 0:
                        if FM:
                            self.choices[-1] += "Saw Dealer"
                            path += "Saw Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )
                    
                    # На последний патрон - просто бьём
                    elif LR == 1:
                        if FM:
                            self.choices[-1] += "Dealer"
                            path += "Dealer"
                        self.EV[-1] += ch
                        self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )
                    
                    # Тратим предметы, пытаясь пропустить раунд
                    else:

                        # Если дилер не убивает на своём ходе
                        if Simulation.can_kill( [ YHP, LR - 1, BL, MI, HI ] ) == 0:

                            # По EV мы впереди: 2 в него 1 в себя
                            if LR == 3 and HI["Handcuffs"] == 0:
                                if FM:
                                    self.choices[-1] += "Dealer"
                                    path += "Dealer"
                                self.EV[-1] += ch
                                self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )

                            # Иначе скипаем патрон для норм ситуации (не тратим адреналин)
                            elif MI["Beer"] != 0:
                                if FM:
                                    self.choices[-1] += "Beer "
                                    path += "Beer "
                                MI["Beer"] = MI["Beer"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )
                            
                            elif MI["Inverter"] != 0:
                                if FM:
                                    self.choices[-1] += "Inverter "
                                    path += "Inverter "
                                MI["Inverter"] = MI["Inverter"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                            # Иначе просто стреляем
                            else:
                                if FM:
                                    self.choices[-1] += "Dealer"
                                    path += "Dealer"
                                self.EV[-1] += ch
                                self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )

                        # Пытаемся выжить
                        else:
                            if MI["Beer"] != 0:
                                if FM:
                                    self.choices[-1] += "Beer "
                                    path += "Beer "
                                MI["Beer"] = MI["Beer"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )
                            
                            elif MI["Inverter"] != 0:
                                if FM:
                                    self.choices[-1] += "Inverter "
                                    path += "Inverter "
                                MI["Inverter"] = MI["Inverter"] - 1
                                self.me_calculate( self, [YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM] )
                            
                            elif HI["Inverter"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Inverter "
                                    path += "Inverter "
                                MI["Adrenalin"] = MI["Adrenalin"] - 1
                                HI["Inverter"] = HI["Inverter"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM] )
                            
                            elif HI["Beer"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Beer "
                                    path += "Beer "
                                MI["Adrenalin"] = MI["Adrenalin"] - 1
                                HI["Beer"] = HI["Beer"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                            else:

                                # Увы и ах
                                if FM:
                                    self.choices[-1] += "Dealer"
                                    path += "Dealer"
                                self.EV[-1] += ch
                                self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )
                
                elif DHP == 3:

                    # Наручники + Пила
                    if LR >= 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and MI["Saw"] + \
                                     min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Handcuffs"] ), HI["Saw"] ) != 0
                                   ):
                        if FM:
                            self.choices[-1] += "Handcuffs Saw Dealer Dealer"
                            path += "Handcuffs Saw Dealer Dealer"
                        self.EV[-1] += ch * 3
                        self.dealer_calculate( self, [ YHP, DHP - 3, LR - 2, BL, ch, path, MI, HI, False ] )

                    # На 2 последних патрона Наручники
                    elif LR == 2 and MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0:
                        if FM:
                            self.choices[-1] += "Handcuffs Dealer Dealer"
                            path += "Handcuffs Dealer Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR - 2, BL, ch, path, MI, HI, False ] )
                    
                    # На последний патрон Пила
                    elif LR == 1 and ( MI["Saw"] + min( MI["Adrenalin"], HI["Saw"] ) != 0 ):
                        if FM:
                            self.choices[-1] += "Saw Dealer"
                            path += "Saw Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )
                    
                    else: # Тратим предметы для скипа

                         # Если диллер не убивает на своём ходе
                        if Simulation.can_kill( [ YHP, LR - 1, BL, MI, HI ] ) == 0:

                            # Наручники сразу используем т.к. их использование всегда выгодно
                            if HI["Handcuffs"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Handcuffs Dealer Dealer"
                                    path += "Handcuffs Dealer Dealer"
                                HI["Handcuffs"] = HI["Handcuffs"] - 1
                                MI["Adrenalin"] = MI["Adrenalin"] - 1
                                self.EV[-1] += ch * 2
                                self.dealer_calculate( self, [ YHP, DHP - 2, LR - 2, BL, ch, path, MI, HI, False ] )
                            
                            elif HI["Handcuffs"] != 0:
                                if FM:
                                    self.choices[-1] += "Handcuffs Dealer Dealer"
                                    path += "Handcuffs Dealer Dealer"
                                MI["Handcuffs"] = MI["Handcuffs"] - 1
                                self.EV[-1] += ch * 2
                                self.dealer_calculate( self, [ YHP, DHP - 2, LR - 2, BL, ch, path, MI, HI, False ] )

                            # Используем пилу или просто бьём когда патронов нечётно
                            elif LR == 3 and HI["Handcuffs"] == 0:

                                # Используем пилу
                                if HI["Saw"] != 0 and MI["Adrenalin"] != 0:
                                    if FM:
                                        self.choices[-1] += "Saw Dealer"
                                        path += "Saw Dealer"
                                    HI["Saw"] = HI["Saw"] - 1
                                    MI["Adrenalin"] = MI["Adrenalin"] - 1
                                    self.EV[-1] += ch * 2
                                    self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )

                                elif MI["Saw"] != 0:
                                    if FM:
                                        self.choices[-1] += "Saw Dealer"
                                        path += "Saw Dealer"
                                    MI["Saw"] = MI["Saw"] - 1
                                    self.EV[-1] += ch * 2
                                    self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )
                                
                                # Просто бьём
                                else:
                                    if FM:
                                        self.choices[-1] += "Dealer"
                                        path += "Dealer"
                                    self.EV[-1] += ch
                                    self.dealer_calculate( self, [YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )
                            
                            # Иначе пробуем скипнуть патрон
                            else:
                                if MI["Beer"] != 0:
                                    if FM:
                                        self.choices[-1] += "Beer "
                                        path += "Beer "
                                    MI["Beer"] = MI["Beer"] - 1
                                    self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                                elif MI["Inverter"] != 0:
                                    if FM:
                                        self.choices[-1] += "Inverter "
                                        path += "Inverter "
                                    MI["Inverter"] = MI["Inverter"] - 1
                                    self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )
                                
                                # Если не получилось используем пилу/стреляем
                                elif HI["Saw"] != 0 and MI["Adrenalin"] != 0:
                                    if FM:
                                        self.choices[-1] += "Saw Dealer"
                                        path += "Saw Dealer"
                                    HI["Saw"] = HI["Saw"] - 1
                                    MI["Adrenalin"] = MI["Adrenalin"] - 1
                                    self.EV[-1] += ch * 2
                                    self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )
                                
                                elif MI["Saw"] != 0:
                                    if FM:
                                        self.choices[-1] += "Saw Dealer"
                                        path += "Saw Dealer"
                                    MI["Saw"] = MI["Saw"] - 1
                                    self.EV[-1] += ch * 2
                                    self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )

                                # Просто бьём
                                else:
                                    if FM:
                                        self.choices[-1] += "Dealer"
                                        path += "Dealer"
                                    self.EV[-1] += ch
                                    self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )

                        # Пробуем выжить
                        else:
                            if MI["Beer"] != 0:
                                if FM:
                                    self.choices[-1] += "Beer "
                                    path += "Beer "
                                MI["Beer"] = MI["Beer"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM] )

                            elif MI["Inverter"] != 0:
                                if FM:
                                    self.choices[-1] += "Inverter "
                                    path += "Inverter "
                                MI["Inverter"] = MI["Inverter"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                            elif HI["Inverter"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Inverter "
                                    path += "Inverter "
                                MI["Adrenalin"] = MI["Adrenalin"] - 1
                                HI["Inverter"] = HI["Inverter"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                            elif HI["Beer"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Beer "
                                    path += "Beer "
                                MI["Adrenalin"] = MI["Adrenalin"] - 1
                                HI["Beer"] = HI["Beer"] - 1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                            else:
                                if FM:
                                    self.choices[-1] += "Dealer"
                                    path += "Dealer"

                                # Надеемся на лучшее
                                self.EV[-1] += ch
                                self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )

                else: # DHP == 4

                    # Наручники + 2 Пилы
                    if LR >= 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and MI["Saw"] + \
                                     min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Handcuffs"] ), HI["Saw"] ) > 1
                                   ):
                        if FM:
                            self.choices[-1] += "Handcuffs Saw Dealer Saw Dealer"
                            path += "Handcuffs Saw Dealer Saw Dealer"
                        self.EV[-1] += ch * 4
                        self.dealer_calculate( self, [ YHP, DHP - 4, LR - 2, BL, ch, path, MI, HI, False ] )

                    # На 2 патрона Наручники + Пила
                    elif BL == 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and MI["Saw"] + \
                                       min( MI["Adrenalin"] - Simulation.use_adrenalin(1, MI["Handcuffs"] ), HI["Saw"] ) != 0
                                     ):
                        if FM:
                            self.choices[-1] += "Handcuffs Saw Dealer Dealer"
                            path += "Handcuffs Saw Dealer Dealer"
                        self.EV[-1] += ch * 3
                        self.dealer_calculate( self, [ YHP, DHP - 3, LR - 2, BL, ch, path, MI, HI, False ] )

                    # На 2 патрона Наручники
                    elif BL == 2 and ( MI["Handcuffs"] + min( MI["Adrenalin"], HI["Handcuffs"] ) != 0 and MI["Inverter"] + \
                                       min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Saw"] ), HI["Inverter"] ) > 1
                                     ):
                        if FM:
                            self.choices[-1] += "Handcuffs Dealer Dealer"
                            path += "Handcuffs Dealer Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR - 2, BL, ch, path, MI, HI, False ] )
                    
                    # На последний патрон Пила
                    elif BL == 1 and ( MI["Saw"] + min( MI["Adrenalin"], HI["Saw"] ) != 0 and MI["Inverter"] + \
                                       min( MI["Adrenalin"] - Simulation.use_adrenalin( 1, MI["Saw"] ), HI["Inverter"] ) != 0
                                     ):
                        if FM:
                            self.choices[-1] += "Saw Dealer"
                            path += "Saw Dealer"
                        self.EV[-1] += ch * 2
                        self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )
                    
                    # Пробуем скипнуть патроны для комбы
                    else:

                        # Если диллер не убивает на своём ходе
                        if Simulation.can_kill( [ YHP, LR - 1, BL, MI, HI ] ) == 0:

                            # Используем наручники и пилу поскольку это всегда выгодно
                            if HI["Handcuffs"] != 0 and HI["Saw"] != 0 and MI["Adrenalin"] > 1:
                                if FM:
                                    self.choices[-1] += "Handcuffs Saw Dealer Dealer"
                                    path += "Handcuffs Saw Dealer Dealer"
                                HI["Handcuffs"] = HI["Handcuffs"] - 1
                                HI["Saw"] = HI["Handcuffs"] - 1
                                MI["Adrenalin"] -= 2
                                self.EV[-1] += ch * 3
                                self.dealer_calculate( self, [ YHP, DHP - 3, LR - 2, BL, ch, path, MI, HI, False ] )

                            elif HI["Handcuffs"] != 0 and MI["Saw"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Handcuffs Saw Dealer Dealer"
                                    path += "Handcuffs Saw Dealer Dealer"
                                HI["Handcuffs"]-=1
                                MI["Saw"]-=1
                                MI["Adrenalin"]-=1
                                self.EV[-1] += ch * 3
                                self.dealer_calculate( self, [ YHP, DHP - 3, LR - 2, BL, ch, path, MI, HI, False ] )

                            elif MI["Handcuffs"] != 0 and HI["Saw"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Handcuffs Saw Dealer Dealer"
                                    path += "Handcuffs Saw Dealer Dealer"
                                MI["Handcuffs"]-=1
                                HI["Saw"]-=1
                                MI["Adrenalin"]-=1
                                self.EV[-1] += ch * 3
                                self.dealer_calculate( self, [ YHP, DHP - 3, LR - 2, BL, ch, path, MI, HI, False ] )
                            
                            elif MI["Handcuffs"] != 0 and MI["Saw"] != 0:
                                if FM:
                                    self.choices[-1] += "Handcuffs Saw Dealer Dealer"
                                    path += "Handcuffs Saw Dealer Dealer"
                                MI["Handcuffs"]-=1
                                MI["Saw"]-=1
                                self.EV[-1] += ch * 3
                                self.dealer_calculate( self, [ YHP, DHP - 3, LR - 2, BL, ch, path, MI, HI, False ] )

                            # Используем наручники
                            elif HI["Handcuffs"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Handcuffs Dealer Dealer"
                                    path += "Handcuffs Dealer Dealer"
                                HI["Handcuffs"]-=1
                                MI["Adrenalin"]-=1
                                self.EV[-1] += ch * 2
                                self.dealer_calculate( self, [ YHP, DHP - 2, LR - 2, BL, ch, path, MI, HI, False ] )

                            elif HI["Handcuffs"] != 0:
                                if FM:
                                    self.choices[-1] += "Handcuffs Dealer Dealer"
                                    path += "Handcuffs Dealer Dealer"
                                MI["Handcuffs"]-=1
                                self.EV[-1] += ch * 2
                                self.dealer_calculate( self, [ YHP, DHP - 2, LR - 2, BL, ch, path, MI, HI, False ] )
                            
                            # Используем пилу и просто бьём когда патроно нечётно
                            elif LR == 3 and HI["Handcuffs"] == 0:

                                # Используем пилу
                                if HI["Saw"] != 0 and MI["Adrenalin"] != 0:
                                    if FM:
                                        self.choices[-1] += "Saw Dealer"
                                        path += "Saw Dealer"
                                    HI["Saw"]-=1
                                    MI["Adrenalin"]-=1
                                    self.EV[-1] += ch * 2
                                    self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )

                                elif MI["Saw"] != 0:
                                    if FM:
                                        self.choices[-1] += "Saw Dealer"
                                        path += "Saw Dealer"
                                    MI["Saw"]-=1
                                    self.EV[-1] += ch * 2
                                    self.dealer_calculate( self [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )
                                
                                # Просто бьём
                                else:
                                    if FM:
                                        self.choices[-1] += "Dealer"
                                        path += "Dealer"
                                    self.EV[-1] += ch
                                    self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )

                            # Пробуем скипнуть патрон
                            else:
                                if MI["Beer"] != 0:
                                    if FM:
                                        self.choices[-1] += "Beer "
                                        path += "Beer "
                                    MI["Beer"]-=1
                                    self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                                elif MI["Inverter"] != 0:
                                    if FM:
                                        self.choices[-1] += "Inverter "
                                        path += "Inverter "
                                    MI["Inverter"]-=1
                                    self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )
                                
                                # Если не получилось используем пилу/стреляем
                                elif HI["Saw"] != 0 and MI["Adrenalin"] != 0:
                                    if FM:
                                        self.choices[-1] += "Saw Dealer"
                                        path += "Saw Dealer"
                                    HI["Saw"]-=1
                                    MI["Adrenalin"]-=1
                                    self.EV[-1] += ch * 2
                                    self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )
                                
                                elif MI["Saw"] != 0:
                                    if FM:
                                        self.choices[-1] += "Saw Dealer"
                                        path += "Saw Dealer"
                                    MI["Saw"]-=1
                                    self.EV[-1] += ch * 2
                                    self.dealer_calculate( self, [ YHP, DHP - 2, LR - 1, BL, ch, path, MI, HI, False ] )
                                
                                # Просто бьём
                                else:
                                    if FM:
                                        self.choices[-1] += "Dealer"
                                        path += "Dealer"
                                    self.EV[-1] += ch
                                    self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )

                        # Пробуем скипнуть патрон
                        else:
                            if MI["Beer"] != 0:
                                if FM:
                                    self.choices[-1] += "Beer "
                                    path += "Beer "
                                MI["Beer"]-=1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                            elif MI["Inverter"] != 0:
                                if FM:
                                    self.choices[-1] += "Inverter "
                                    path += "Inverter "
                                MI["Inverter"]-=1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )
                            
                            elif HI["Inverter"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Inverter "
                                    path += "Inverter "
                                    MI["Adrenalin"]-=1
                                    HI["Inverter"]-=1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                            elif HI["Beer"] != 0 and MI["Adrenalin"] != 0:
                                if FM:
                                    self.choices[-1] += "Beer "
                                    path += "Beer "
                                MI["Adrenalin"]-=1
                                HI["Beer"]-=1
                                self.me_calculate( self, [ YHP, DHP, LR - 1, BL, ch, path, MI, HI, FM ] )

                            else:

                                # Надеемся на лучшее
                                if FM:
                                    self.choices[-1] += "Dealer"
                                    path += "Dealer"
                                self.EV[-1] += ch
                                self.dealer_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch, path, MI, HI, False ] )

    '''
    self - результаты, game_params - игровые показатели
    '''

    # Задача 1. Добавить логику предметам
    def dealer_calculate( self, game_params ):

        '''
        Игровые показатели:
        YHP - здоровье игрока, DHP - здоровье дилера, LR - боевые патроны, BL - холостые патроны,
        CH - вероятность события, PATH - путь действий, MI - предметы игрока, HI - предметы дилера,
        FM - первый ход
        '''

        if self == None or len(game_params) != 9:
            return

        YHP = game_params[0]
        DHP = game_params[1]
        LR = game_params[2]
        BL = game_params[3]
        ch = game_params[4]
        path = game_params[5]
        MI = game_params[6]
        HI = game_params[7]
        FM = game_params.FM[8]

        # Условия завершения рекурсии
        # 1. Кто-то умер
        if YHP < 1:
            self.lose[ self.choices.IndexOf(path) ] += ch
        elif DHP < 1:
            self.win[ self.choices.IndexOf(path) ] += ch

        # 2. Кончились патроны
        elif LR + BL != 0:

            # Шанс боевого патрона
            damage = LR / ( LR + BL )

            # Боевых больше холостых /1 HP при наличии боевых - в меня
            if LR > BL or ( DHP == 1 and LR != 0 ):
                self.EV[ self.choices.IndexOf(path) ] -= ch * damage
                self.me_calculate( self, [ YHP - 1, DHP, LR - 1, BL, ch * damage, path, MI, HI, FM ] )
                if (BL != 0):
                    self.me_calculate( self, [ YHP, DHP, LR, BL - 1, ch * ( 1 - damage ), path, MI, HI, FM ] )
            
            # Иначе - в себя
            else:
                self.EV[ self.choices.IndexOf(path) ] += ch * damage
                if (LR != 0):
                    self.me_calculate( self, [ YHP, DHP - 1, LR - 1, BL, ch * damage, path, MI, HI, FM ] )
                self.dealer_calculate( self, [ YHP, DHP, LR, BL - 1, ch * (1 - damage), path, MI, HI, FM ] )