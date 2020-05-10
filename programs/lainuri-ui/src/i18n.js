const i18n_messages = {
/*
  ENGLISH-ENGLISH
*/
  en: {
    RFID_tags_found: "RFID Tags found",
    App: {
      Check_in: "Return",
      Check_out: "Check out",
    },
    CheckIn: {
      Checking_in: "Returning",
      Place_items_on_the_reader_and_read_barcodes: "Place items on the reader platform or read barcodes",
      Finish: "Finish",
      "Finish+Receipt": "Finish + Receipt",
      Your_Check_ins: "Your returns",
      In_Queue: "In queue",
      Errors: "Errors",
      Place_to_bin_OK: "Place to shelf 'normal'",
      Place_to_bin_ODD: "Place to shelf 'strange'",
    },
    CheckOut: {
      Checking_out: "Checking out",
      Place_items_on_the_reader_and_read_barcodes: "Place items on the reader platform or read barcodes",
      Read_library_card: "Read libary card",
      "Hi_user!": "Hi {user}!",
      Return: "Return",
      Finish: "Finish",
      "Finish+Receipt": "Finish + Receipt",
      Your_Check_outs: "Your loans",
      In_Queue: "In queue",
      Errors: "Errors",
      Check_out_failed: "Checkout failed",
      'Be_advised!': "Be advised!",
    },
    Exception: {
      ILSConnectionFailure: "Connection to the library system temporarily failed. Please try again.",
      RFIDCommand: "Place the item on the reader, setting security gate status failed",
      TagNotDetected: "Place the item on the reader, setting security gate status failed",
      GateSecurityStatusVerification: "Place the item on the reader, setting security gate status failed",
      InvalidUser: "Authentication failed",
      NoUser: "Unknown user",
      NoItem: "Unknown item",
      NoItemIdentifier: "Unknown item is missing identifier",
      SessionTimeout: "Session timeout",
    },
    MainMenuView: {
      RFID_tags_found: "RFID Tags found",
    },
    PrintNotification: {
      Take_the_receipt: "Take the receipt",
    },
    State: {
      not_checked_out: "Not checked out?",
      return_to_another_branch: "To transport",
      needs_confirmation: "Cannot be loaned here",
      outstanding_fines: "Found outstanding fines",
      checkout_impossible: "Check out is impossible!",

      'Checkout::Renew': "Already checked out to you",
      'Item::CheckedOut': "Item is already checked out by somebody else",
    },
    StatusBar: {
      Lainuri_server_connection_lost: "Lainuri",
      Printer_off: "Printer",
      Printer_paper_runout: "Paper out",
      Printer_paper_low: "Paper low",
      Printer_receipt_not_torn: "Receipt",
      RFID_reader_off: "RFID",
      Barcode_reader_off: "Barcode",
      ILS_connection_lost: "ILS lost",
    },
  },
/*
  FINNISH-FINNISH
*/
  fi: {
    App: {
      Check_in: "Palauta",
      Check_out: "Lainaa",
    },
    CheckIn: {
      Checking_in: "Palautetaan",
      Place_items_on_the_reader_and_read_barcodes: "Aseta niteet lukulevylle tai lue viivakoodeja",
      Finish: "Lopeta",
      "Finish+Receipt": "Lopeta + Kuitti",
      Your_Check_ins: "Palautuksesi",
      In_Queue: "Jonossa",
      Errors: "Virheet",
      Place_to_bin_OK: "Paikka hyllyyn 'normaali'",
      Place_to_bin_ODD: "Paikka hyllylle 'outo'",
    },
    CheckOut: {
      Checking_out: "Lainataan",
      Place_items_on_the_reader_and_read_barcodes: "Aseta niteet lukulevylle tai lue viivakoodeja",
      Read_library_card: "Lue kirjastokortti",
      "Hi_user!": "Moi {user}!",
      Return: "Palaa",
      Finish: "Lopeta",
      "Finish+Receipt": "Lopeta + Kuitti",
      Your_Check_outs: "Lainasi",
      In_Queue: "Jonossa",
      Errors: "Virheet",
      Check_out_failed: "Lainaaminen epäonnistui",
      'Be_advised!': "Huomioikaa!",
    },
    Exception: {
      ILSConnectionFailure: "Yhteys kirjastojärjestelmään epäonnistui. Yritä uudelleen.",
      RFIDCommand: "Laita nide lukijalle, hälyttimen asettaminen epäonnistui!",
      TagNotDetected: "Laita nide lukijalle, hälyttimen asettaminen epäonnistui!",
      GateSecurityStatusVerification: "Laita nide lukijalle, hälyttimen asettaminen epäonnistui!",
      InvalidUser: "Kirjautuminen epäonnistui",
      NoUser: "Tuntematon käyttäjä",
      NoItem: "Tuntematon nide",
      NoItemIdentifier: "Tuntematon nide ilman tunnistetta",
      SessionTimeout: "Istunnon aikakatkaisu",
    },
    MainMenuView: {
      RFID_tags_found: "RFID tägit löydetty",
    },
    PrintNotification: {
      Take_the_receipt: "Ota kuitti",
    },
    State: {
      not_checked_out: "Ei lainattu?",
      return_to_another_branch: "Lähtee kuljetukseen",
      needs_confirmation: "Ei voida lainata tässä",
      outstanding_fines: "Maksamattomia maksuja",
      checkout_impossible: "Lainaaminen mahdotonta",

      'Checkout::Renew': "Jo lainassa teillä",
      'Item::CheckedOut': "Tämä nide on jo lainassa jollakulla muulla",
    },
    StatusBar: {
      Lainuri_server_connection_lost: "Bäkkärivirhe",
      Printer_off: "Tulostin",
      Printer_paper_runout: "Paperi loppu",
      Printer_paper_low: "Paperi vähissä",
      Printer_receipt_not_torn: "Kuitti",
      RFID_reader_off: "RFID",
      Barcode_reader_off: "Viivakoodi",
      ILS_connection_lost: "Kirjastojärjestelmä hävisi",
    },
  },
/*
  SWEDISH-SWEDISH
*/
  sv: {
    App: {
      Check_in: "Kolla in",
      Check_out: "Kolla upp",
    },
    CheckIn: {
      Checking_in: "Checka in",
      Place_items_on_the_reader_and_read_barcodes: "Placera artiklar på läsarplattformen eller läs streckkoder",
      Finish: "Sluta",
      "Finish+Receipt": "Sluta + Kvitto",
      Your_Check_ins: "Dina checkins",
      In_Queue: "I kö",
      Errors: "Misstag",
      Place_to_bin_OK: "Plats på hyllan 'normal'",
      Place_to_bin_ODD: "Plats att hyllas 'konstigt'",
    },
    CheckOut: {
      Checking_out: "Checkar ut",
      Read_library_card: "Läs bibliotekskortet",
      "Hi_user!": "Hej {user}!",
      Place_items_on_the_reader_and_read_barcodes: "Placera artiklar på läsarplattformen eller läs streckkoder",
      Return: "Återvända",
      Finish: "Sluta",
      "Finish+Receipt": "Sluta + Kvitto",
      Your_Check_outs: "Dina utcheckningar",
      In_Queue: "I kö",
      Errors: "Misstag",
      Check_out_failed: "Utcheckning misslyckas",
      'Be_advised!': "Rådas!",
    },
    Exception: {
      ILSConnectionFailure: "Anslutningen till bibliotekssystemet misslyckades tillfälligt. Var god försök igen.",
      RFIDCommand: "Placera objektet på läsaren och ställa in säkerhetsgrindens status misslyckades",
      TagNotDetected: "Placera objektet på läsaren och ställa in säkerhetsgrindens status misslyckades",
      GateSecurityStatusVerification: "Placera objektet på läsaren och ställa in säkerhetsgrindens status misslyckades",
      InvalidUser: "Autentisering misslyckades",
      NoUser: "Okänd användare",
      NoItem: "Okänd artikel",
      NoItemIdentifier: "Okänt objekt saknas ID",
      SessionTimeout: "Sessionen har gått ut",
    },
    MainMenuView: {
      RFID_tags_found: "RFID-taggar hittade",
    },
    PrintNotification: {
      Take_the_receipt: "Ta kvittot",
    },
    State: {
      not_checked_out: "Inte utcheckad?",
      return_to_another_branch: "Att transportera",
      needs_confirmation: "Kan inte lånas här",
      outstanding_fines: "Hittade utestående böter",
      checkout_impossible: "Kolla ut är omöjligt",

      'Checkout::Renew': "Har redan checkat ut för dig",
      'Item::CheckedOut': "Varan har redan checkats ut av någon annan",
    },
    StatusBar: {
      Lainuri_server_connection_lost: "Servern förlorad",
      Printer_off: "Skrivaren av",
      Printer_paper_runout: "Papper sprang ut",
      Printer_paper_low: "Papper låg",
      Printer_receipt_not_torn: "Kvitto kvar",
      RFID_reader_off: "RFID av",
      Barcode_reader_off: "Streckkod av",
      ILS_connection_lost: "ILS förlorade",
    },
  },
/*
  RUSSIAN-RUSSIAN
*/
  ru: {
    App: {
      Check_in: "Возвращение",
      Check_out: "одолжить",
    },
    CheckIn: {
      Checking_in: "Регистрация в",
      Place_items_on_the_reader_and_read_barcodes: "Размещайте предметы на платформе считывателя или считывайте штрих-коды",
      Finish: "Стоп",
      "Finish+Receipt": "Стоп + Чек",
      Your_Check_ins: "Ваши возвращения",
      In_Queue: "Ваши чеки",
      Errors: "ошибки",
      Place_to_bin_OK: "Место на полке 'нормально'",
      Place_to_bin_ODD: "Место на полке 'странно'",
    },
    CheckOut: {
      Checking_out: "Проверка",
      Place_items_on_the_reader_and_read_barcodes: "Размещайте предметы на платформе считывателя или считывайте штрих-коды",
      Read_library_card: "Читать библиотечную карточку",
      "Hi_user!": "Здравствуй {user}!",
      Return: "Возвращение",
      Finish: "Стоп",
      "Finish+Receipt": "Стоп + Чек",
      Your_Check_outs: "Ваши кредиты",
      In_Queue: "Ваши чеки",
      Errors: "ошибки",
      Check_out_failed: "Не удалось оформить заказ",
      Be_advised: "Быть посоветованным",
    },
    Exception: {
      ILSConnectionFailure: "Подключение к библиотечной системе временно не удалось. Пожалуйста, попробуйте еще раз.",
      RFIDCommand: "Поместите элемент в считыватель, установка состояния ворот безопасности не удалась",
      TagNotDetected: "Поместите элемент в считыватель, установка состояния ворот безопасности не удалась",
      GateSecurityStatusVerification: "Поместите элемент в считыватель, установка состояния ворот безопасности не удалась",
      InvalidUser: "Ошибка аутентификации",
      NoUser: "Неизвестный пользователь",
      NoItem: "Неизвестный предмет",
      NoItemIdentifier: "Неизвестный предмет отсутствует идентификатор",
      SessionTimeout: "Тайм-аут сеанса",
    },
    MainMenuView: {
      RFID_tags_found: "RFID метки найдены",
    },
    PrintNotification: {
      Take_the_receipt: "Возьмите квитанцию",
    },
    State: {
      not_checked_out: "Не проверено",
      return_to_another_branch: "Для транзита",
      needs_confirmation: "Здесь нельзя одолжить",
      outstanding_fines: "Нашел выдающиеся штрафы",
      checkout_impossible: "Проверить невозможно",

      'Checkout::Renew': "Уже проверил для вас",
      'Item::CheckedOut': "Товар уже был проверен кем-то другим",
    },
    StatusBar: {
      Lainuri_server_connection_lost: "Сервер потерян",
      Printer_off: "Принтер выключен",
      Printer_paper_runout: "Бумага закончилась",
      Printer_paper_low: "Бумага низкая",
      Printer_receipt_not_torn: "Квитанция слева",
      RFID_reader_off: "RFID выключен",
      Barcode_reader_off: "Штрих-код выключен",
      ILS_connection_lost: "ILS потерял",
    },
  },
};

export {i18n_messages}