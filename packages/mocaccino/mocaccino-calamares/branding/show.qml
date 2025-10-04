/* === This file is part of Calamares - <http://github.com/calamares> ===
 *
 *   Copyright 2015, Teo Mrnjavac <teo@kde.org>
 *
 *   Calamares is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   Calamares is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with Calamares. If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    Timer {
        interval: 5000 // Set to 5 seconds (5000ms) for each slide
        running: true
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    // --------------------------------------------------
    // START OF CUSTOM SLIDES
    // --------------------------------------------------

    // MOS_1: MocaccinoOS Logo / Layers (Initial Image)
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_1.jpg"
            anchors.fill: parent
        }
    }

    // MOS_2: Office Work
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_2.jpg"
            anchors.fill: parent
        }
    }

    // MOS_3: Gaming
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_3.jpg"
            anchors.fill: parent
        }
    }

    // MOS_4: Developer
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_4.jpg"
            anchors.fill: parent
        }
    }

    // MOS_5: Conference Call
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_5.jpg"
            anchors.fill: parent
        }
    }

    // MOS_6: Super Speed
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_6.jpg"
            anchors.fill: parent
        }
    }

    // MOS_7: Secure
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_7.jpg"
            anchors.fill: parent
        }
    }

    // MOS_8: SDR / Radio Astronomy
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_8.jpg"
            anchors.fill: parent
        }
    }

    // MOS_9: Design & Create
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_9.jpg"
            anchors.fill: parent
        }
    }

    // MOS_10: Support Us / Donate (IMPORTANT: Donate link)
    Slide {
        anchors.fill: parent
        Image {
            source: "images/MOS_10.jpg"
            anchors.fill: parent
        }
    }
    // --------------------------------------------------
    // END OF CUSTOM SLIDES
    // --------------------------------------------------
}
