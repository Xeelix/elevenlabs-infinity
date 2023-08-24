from voice_gen.api_utils.eleven_api import ElevenLabsLimitException
from voice_gen.audio.eleven_voice_module import ElevenLabsVoiceModule

from voice_gen.evenlab_regger import regger


# Write api key to file
def write_key_to_file(key):
    with open("evenlab_key.txt", "w") as f:
        f.write(key)


def generate_voice(text):
    # Load key from file
    with open("evenlab_key.txt", "r") as f:
        evenlab_key = f.read()

    print("generating voice...")

    voice_module = ElevenLabsVoiceModule(api_key=evenlab_key, voiceName="Antoni", checkElevenCredits=True)

    while True:
        try:
            voice_module.generate_voice(text, "test.mp3")
            print(f"Now available credits: {voice_module.get_remaining_characters()}")
            break
        except ElevenLabsLimitException:
            print(f"ElevenLabs API KEY doesn't have enough credits, now is:  {voice_module.get_remaining_characters()}")

            # Get new api via Selenium
            evenlab_key = regger.register()
            write_key_to_file(evenlab_key)
            print(f"New API KEY: {evenlab_key}")
            voice_module = ElevenLabsVoiceModule(api_key=evenlab_key, voiceName="Antoni", checkElevenCredits=True)

    print("Voice generated")


if __name__ == '__main__':
    generate_voice("Я пришел за тобой! Обернись!!!")
