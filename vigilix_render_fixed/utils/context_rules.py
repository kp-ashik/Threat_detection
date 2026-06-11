def allowed_alert_for_location(location_type, label):
    text = label.lower()
    location = location_type.lower()

    weapon_words = ["weapon", "gun", "knife", "sharp object"]
    crowd_words = ["crowd", "crowd gathering"]

    if location == "school":
        return any(word in text for word in weapon_words + crowd_words)

    if location == "college":
        return True

    if location == "mall":
        allowed = weapon_words + crowd_words + ["fire", "smoke", "theft", "steal", "restricted item"]
        return any(word in text for word in allowed)

    if location == "railway station":
        allowed = weapon_words + crowd_words + ["fire", "smoke", "theft", "steal", "restricted item"]
        return any(word in text for word in allowed)

    if location == "road":
        allowed = ["helmet", "triple riding", "seat belt", "speed", "vehicle", "motorcycle", "car", "crowd"]
        return any(word in text for word in allowed)

    return True
