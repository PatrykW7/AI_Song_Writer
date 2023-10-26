import gradio as gr
import gpt_2_simple as gpt2


def pipeline(prompt: str, length: int, temperature: float, top_k: int, top_p: float):
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess)
    lyrics = gpt2.generate(
        sess,
        return_as_list=True,
        length=length,
        prefix=prompt,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
    )[0]
    return lyrics


length_slider = gr.inputs.Slider(
    minimum=50, maximum=1000, default=500, label="Lyrics length"
)
temperature_slider = gr.inputs.Slider(
    minimum=0.6, maximum=1.0, default=0.7, label="Temperature"
)
top_k_slider = gr.inputs.Slider(minimum=0, maximum=40, default=0, label="Top k")
top_p_slider = gr.inputs.Slider(minimum=0.0, maximum=1.0, default=0.9, label="Top p")

app = gr.Interface(
    fn=pipeline,
    inputs=["text", length_slider, temperature_slider, top_k_slider, top_p_slider],
    outputs="text",
)

if __name__ == "__main__":
    app.launch(debug=True)
