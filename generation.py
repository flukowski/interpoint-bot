from numpy.random import choice


async def get_random_build(message):
  build_message = ''
  build_message += random_mech()
  build_message += '\n\n'
  build_message += random_trait()
  build_message += '\n'
  build_message += random_trait()
  build_message += '\n'
  build_message += random_trait()
  build_message += '\n\n'
  build_message += random_cp()

  return await message.channel.send(build_message)


async def get_random_mech(message):
  return await message.channel.send(random_mech())


def random_mech():
  mechs = ["Everest", "Sagarmatha", "Blackbeard", "Drake", "Lancaster", "Nelson", "Raleigh", "Tortuga", "Vlad", "Caliban", "Zheng", "Kidd", "Black Witch", "Death's Head", "Dusk Wing", "Metal Mark", "Monarch", "Mourning Cloak", "Swallowtail", "Ranger Swallowtail", "Atlas", "Balor", "Goblin", "Gorgon", "Hydra", "Manticore", "Minotaur", "Pegasus", "Kobold", "Lich", "Barbarossa", "Ghengis", "Ghengis Mk1", "Iskander", "Napoleon", "Saladin", "Sherman", "Tokugawa", "Enkidu", "Sunzi"]
  mech = choice(mechs)
  return mech


async def get_random_trait(message):
  return await message.channel.send(random_trait())


def random_trait():
  traits = [ "Iniative Everest", "Replacable Parts Everest", "Guardian Sagmartha", "Heroism Sagmartha", "Grapple Cable Black Beard", "Lock Kill Sub System Black Beard", "Exposed Reactor Black Beard", "Wrecking Ball Caliban", "Pursue Prey Caliban", "Slam Caliban", "Weak Computer Caliban", "Heavy Frame Drake", "Blast Plating Drake", "Slow Drake", "Guardian Drake", "Reroute Power + Recycle Kidd Lose 1 Trait or Re-Roll this Trait", "Rapid Deployment Kidd", "Insulated Lancaster", "Combat Repair Lancaster", "Redundant System Lancaster", "Momentum Nelson", "Skirmisher Nelson", "Full Metal Jacket Raleigh", "Shielded Magazines Raleigh", "Sentinel Tortuga", "Guardian Tortuga", "Dismemberment Vlad", "Shrike Armor Vlad", "Giant Killer Atlas", "Jäger Dodge Atlas", "Finishing Blow Atlas", "Exposed Reactor Atlas", "Repulser Field Black Witch", "Mag Parry Black Witch", "Neuro Link Deaths Head", "Perfected Targeting Deaths Head", "Manouverability Jets Duskwing", "Harlequin Cloak Duskwing", "Fragile Duskwing", "Flash Cloak Metal Mark", "Carapace Adaption Metal Mark", "Avenger Silos Monarch", "Seeking Payload Monarch", "Hunter Mourning Cloak", "Biotic Components Mourning Cloak", "Integrated Cloak Swallowtail", "Prophetic Scanners Swallowtail", "Scout Battlefield Ranger Swallowtail", "Invigorating Scanners Ranger Swallowtail", "Weathering Ranger Swallowtail", "Self Perpetuating Balor", "Scouring Swarm Balor", "Regenerator Balor", "Liturgycode Goblin", "Reactive Code Goblin", "Fragile Goblin", "Metastatic Paralysis Gorgon", "Gaze Gorgon", "Guardian Gorgon", "System Link Hydra", "Shepherd Field Hydra", "Mimic Carapace Kobold", "Slag Spray Kobold", "Exposed Reactor Kobold", "Soul Vessel Lich", "Immortal Lich (Return to Wreckage instead of Soul Vessel)", "Slag Carapace Manticore", "Unstable System Manticore", "Castigate the Enemies Manticore", "Invert Cockpit Minotaur", "Internal Metafold Minotaur", "Localised Maze Minotaur", "By the Way I know every Pegasus", "Heavy Frame Barbarossa", "Pressure Plating Barbarossa", "Guardian Barbarossa", "Slow Barbarossa", "Insulated Ghengis", "Emergency Vent Ghengis", "Weak Computer Ghengis Mk1", "Insulated Ghengis Mk1", "TBK Munitions Ghengis Mk1", "Assault Launcher Iskander", "Mine Deployer Iskander", "Skeleton Key Iskander", "Heavy Shielding Napoleon", "Flash Aegis Napoleon", "Reinforced Frame Saladin", "Guardian Saladin", "Warp Shield Saladin", "Superior Reactor Sherman", "Marthur Stop Sherman", "Vent Heat Sherman", "Safe Harbor Sunzi", "Anchor Sunzi", "Slip Sunzi", "Limit Break Tokugawa", "Plasma Sheath Tokugawa", "Primal Fury + Talons Enkidu", "All Fours Enkidu", "Brute Strength Enkidu", "Bloodsense Enkidu" ]
  trait = choice(traits)
  return trait


async def get_random_cp(message):
  return await message.channel.send(random_cp())


def random_cp():
  cps = [ "Hyper Spec Fuel Injector Everest", "Raise the Banner Sagarmatha", "Omni Harpoon Blackbeard", "Fortress Protocol Drake", "Latch Drone + Supercharger Lancaster", "Engage Drive + Skirmisher Nelson Lose 1 Trait or Re-Roll this CP", "Mjolnir Cannon + Thunder God Raleigh", "Hyper Reflex Mode Tortuga", "Tormentor Spikes + Shrike Armor Vlad Lose 1 Trait or Re-Roll this CP", "Flayer Shotgun + Equip Autochoke Caliban", "Xiaoli's Tenacity + Xiaoli's Ingenuity Zheng", "Jolly Roger + Skull and Bones Kidd", "Mag Field Black Witch", "Neural Shunt Death's Head", "Hall of Mirrors Dusk Wing", "Tactical Cloak Metal Mark", "Divine Punishment Monarch", "Blinkspace Jump + Stabilize Singularity Mourning Cloak", "Prophetic Interjection Swallowtail", "Grounded + Guerilla Warfare Ranger Swallowtail", "Final Hunt Atlas", "Scouring Swarm + Regeneration + Hive Frenzy Balor Lose 2 Traits or Re-Roll this CP", "Symbiosis Goblin", "Extrude Basilisk Gorgon", "Orochi Drones+Full Deployment Hydra", "Charged Exoskeleton + Destruction of the temple Manticore", "Metafold Maze + Maze Minotaur", "Ushabti Omnigun + Unshackle Ushabti Pegasus", "Terraform Kobold", "Glitch Time Lich", "Apocalypse Rail + Charge Rail Barbarossa", "Expose Powercells Ghengis", "Furiosa + A Pleasure to Burn Ghengis Mk1", "Death Cloud Iskander", "Trueblack Aegis Napoleon", "Tachyon Shield Saladin", "ZF4 Solidcore + Coreburn Protocol Sherman", "Overclock + Radiance Tokugawa", "Crush Limiter Enkidu", "Blink Anchor + Art of War Sunzi" ]
  cp = choice(cps)
  return cp
