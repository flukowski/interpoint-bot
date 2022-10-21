ADMIN_IDS = [202688077351616512, 550523153302945792]
QAZZ_ID = 169544927351537664


def is_from_admin(message):
    return message.author.id in ADMIN_IDS


def is_from_moderator(message):
    """Assumes all admins are also moderators, so you don't need to ask 'is admin or mod'"""
    author_roles = list(map(lambda x: x.name, message.author.roles))
    return is_from_admin(message) or "Moderator" in author_roles


def admin_only(func):
    async def wrapper(message):
        if not is_from_admin(message):
            return await message.channel.send("You are not worthy! Admin only.")
        return await func(message)

    return wrapper


def moderator_only(func):
    async def wrapper(message):
        if not is_from_moderator(message):
            return await message.channel.send("You are not worthy! Moderator only.")
        return await func(message)

    return wrapper
