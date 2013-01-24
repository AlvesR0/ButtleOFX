import QtQuick 1.1


Item {
    id: slider
    implicitWidth : 300
    implicitHeight : 30

    property variant paramObject: model.object


    /* Title of the paramSlider */
    Text {
        id: paramIntTitle
        text: paramObject.text + " : "
        color: "white"
        anchors.top: parent.top
        anchors.verticalCenter: parent.verticalCenter
    }
    // main container
    Rectangle {
        anchors.verticalCenter: parent.verticalCenter
        width: 150
        height: parent.height
        x: paramIntTitle.width + 80
        color: "transparent"

        // The min value (at the beginning of the bar slider)
        Text{
            id: minValue
            x: - 35
            anchors.verticalCenter: parent.verticalCenter
            text: paramObject.minimum
            font.pointSize: 8
            color: "white"
        }
        /* The current value of the slider */
        Text{
            id: currentValue
            x: barSlider.width / 2
            text: paramObject.value
            font.family: "Helvetica"
            font.pointSize: 8
            color: "white"
            y:-2
        }
        // bar slider : one grey, one white
        Rectangle {
            id: barSlider
            anchors.verticalCenter: parent.verticalCenter
            width: 100
            height: 2
            Rectangle{
                id: whiteBar
                x: barSlider.x
                width: cursorSlider.x - barSlider.x
                height: parent.height
                color: "white"
            }
            Rectangle{
                id: greyBar
                x: barSlider.x + cursorSlider.x
                width: barSlider.width - whiteBar.width 
                height: parent.height
                color: "grey"
            }
        }
        // cursor slider (little white rectangle)
        Rectangle {
            id: cursorSlider
            anchors.verticalCenter: parent.verticalCenter
            x: (paramObject.value * barSlider.width) / paramObject.maximum
            height: 10
            width: 5
            radius: 1
            color: "white"
            MouseArea{
                anchors.fill: parent
                drag.target: parent
                drag.axis: Drag.XAxis
                drag.minimumX: barSlider.x// - cursorSlider.width/2
                drag.maximumX: barSlider.x + barSlider.width// - cursorSlider.width/2
                anchors.margins: -10 // allow to have an area around the cursor which allows to select the cursor even if we are not exactly on it
                onReleased: paramObject.value = (cursorSlider.x * paramObject.maximum) / barSlider.width
            }
        }
        // The max value (at the end of the bar slider)
        Text{
            id: maxValue
            x: barSlider.width + 15
            anchors.verticalCenter: parent.verticalCenter
            text: paramObject.maximum
            font.pointSize: 8
            color: "white"
        }
    }
}
