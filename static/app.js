function dump(res) {
    console.log(res)
    document.querySelector('#dumpbox').textContent = res.data.join(", ")
}