# 🚀 HƯỚNG DẪN KIỂM TRA DEMO HỆ THỐNG - NHÓM 04
Học phần: Học máy cơ bản · Giảng viên: Nguyễn Đức Tuấn Anh

---

## 1. Thông tin truy cập Online (24/7)
Hệ thống đã được đóng gói Docker và public qua Ngrok Static Domain vĩnh viễn. Giảng viên và người chấm có thể truy cập trực tiếp từ xa tại:
- **Giao diện Web Frontend:** [https://barmaid-trapezoid-grooving.ngrok-free.dev](https://barmaid-trapezoid-grooving.ngrok-free.dev)
- **Tài liệu API (AI Service Docs):** [https://barmaid-trapezoid-grooving.ngrok-free.dev/docs](https://barmaid-trapezoid-grooving.ngrok-free.dev/docs)

## 2. Các bước kiểm tra nhanh trên giao diện Web
1. Truy cập vào đường link Frontend ở trên.
2. Tại màn hình chính, hệ thống cung cấp **Menu thả xuống (Model Selection)** cho phép chọn 1 trong 4 mô hình học máy:
   - *XGBoost Regressor* (Mô hình tối ưu, $R^2 = 97.89\%$)
   - *Random Forest Regressor* ($R^2 = 97.25\%$)
   - *Linear Regression* (Baseline)
   - *Ridge Regression*
3. Nhập các thông số ngân sách quảng cáo mong muốn cho các kênh (`TV`, `Radio`, `Newspaper`).
4. Bấm nút **"Dự đoán Doanh số"** để nhận kết quả tính toán thời gian thực từ Backend Gateway và AI Service.

## 3. Kiểm tra lịch sử Log & Tracing (Phục vụ bảo vệ Máy 2)
Khi gọi API dự đoán, hệ thống tự động sinh mã `request_id` độc nhất cho từng request, cho phép kiểm tra log theo thời gian thực qua Terminal của Docker:
```bash
docker compose logs -f backend