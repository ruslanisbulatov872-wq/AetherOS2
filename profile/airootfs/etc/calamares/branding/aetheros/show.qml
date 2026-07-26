import QtQuick 2.0

Item {
    id: root
    anchors.fill: parent

    property var slides: [
        { title: "Добро пожаловать в AetherOS",
          text: "Гибкость Arch, простота Ubuntu, красота Mint — в одной системе." },
        { title: "Aether Terminal",
          text: "Мощная командная строка со своими утилитами: aether, aether-info, aether-check." },
        { title: "Aether Package Manager",
          text: "Устанавливайте и обновляйте программы одной командой: aether install <имя>." },
        { title: "Aether Forge",
          text: "Пересобирайте систему под себя — выбирайте компоненты, как в Arch Linux." }
    ]
    property int current: 0

    Rectangle {
        anchors.fill: parent
        color: "#0d1426"
    }

    Column {
        anchors.centerIn: parent
        width: parent.width * 0.8
        spacing: 18

        Text {
            text: root.slides[root.current].title
            color: "#e6ecff"
            font.pixelSize: 28
            font.bold: true
            wrapMode: Text.WordWrap
            width: parent.width
        }
        Text {
            text: root.slides[root.current].text
            color: "#8cc4ff"
            font.pixelSize: 16
            wrapMode: Text.WordWrap
            width: parent.width
        }
    }

    Timer {
        interval: 4000
        running: true
        repeat: true
        onTriggered: root.current = (root.current + 1) % root.slides.length
    }

    function nextSlide() {}
}
