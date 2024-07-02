#include <opencv2/opencv.hpp>
#include <websocketpp/config/asio_no_tls_client.hpp>
#include <websocketpp/client.hpp>
#include <iostream>
#include <thread>
#include <chrono>
#include <base64.h> // Include a Base64 library

typedef websocketpp::client<websocketpp::config::asio_client> client;

class ScreenCapture {
public:
    ScreenCapture(int fps) : fps(fps), cap(cv::VideoCapture(CV_CAP_DSHOW)) {}

    void start_recording() {
        while (true) {
            cv::Mat frame;
            cap >> frame; // Capture frame
            if (frame.empty()) break;

            std::vector<uchar> buf;
            cv::imencode(".png", frame, buf);
            std::string img_str = base64_encode(buf.data(), buf.size());
            send_image(img_str);

            std::this_thread::sleep_for(std::chrono::milliseconds(1000 / fps));
        }
    }

private:
    void send_image(const std::string &image) {
        websocketpp::lib::error_code ec;
        client c;
        client::connection_ptr con = c.get_connection("ws://localhost:8765", ec);
        if (ec) {
            std::cout << "could not create connection because: " << ec.message() << std::endl;
            return;
        }
        c.connect(con);
        c.run();
        con->send(image);
        std::string reply;
        con->recv(reply);
        std::cout << "Status: " << reply << std::endl;
    }

    int fps;
    cv::VideoCapture cap;
};

int main() {
    ScreenCapture screen_capture(120);
    screen_capture.start_recording();
    return 0;
}
