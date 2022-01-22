#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-retrotoons.jarbasai=skill_retrotoons:RetroToonsSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-retrotoons',
    version='0.0.1',
    description='ovos Retro Toons skill plugin',
    url='https://github.com/JarbasSkills/skill-retrotoons',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_retrotoons": ""},
    package_data={'skill_retrotoons': ['locale/*', 'ui/*']},
    packages=['skill_retrotoons'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
