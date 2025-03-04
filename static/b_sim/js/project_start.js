$(document).ready(function () {
   // table_computations
   compute_kpi_table();

   // tooltip behaviour
   $("input[data-content]").hover(
      function () {
         const content = $(this).attr("data-content");
         showTooltip(content, this);
      },
      function () {
         hideTooltip();
      }
   );
});

$(function () {
              $('[data-toggle="popover"]').popover();
          });

function showTooltip(content, element) {
   const tooltipElement = document.createElement("div");
   tooltipElement.className = "tooltip";
   tooltipElement.textContent = content;
   element.after(tooltipElement);
}

// Function to hide tooltip
function hideTooltip() {
   $(".tooltip").remove();
}

function compute_kpi_table() {
   var kpi_table_2_3 = parseFloat($("#kpi_table_2_3").val());
   var kpi_table_3_3 = parseFloat($("#kpi_table_3_3").val());
   if (isNaN(kpi_table_2_3) || isNaN(kpi_table_3_3)) {
      $("#kpi_table_5_3").val("");
      return;
   }
   $("#kpi_table_5_3").val((kpi_table_2_3 * kpi_table_3_3).toFixed(2));

   var kpi_table_5_3 = parseFloat($("#kpi_table_5_3").val());
   var kpi_table_4_4 = parseFloat($("#kpi_table_4_4").val());
   if (isNaN(kpi_table_4_4) || isNaN(kpi_table_5_3)) {
      $("#kpi_table_5_4").val("");
      return;
   }
   var kpi_5_4_result = (kpi_table_5_3 * kpi_table_4_4).toFixed(2);
   $("#kpi_table_5_4").val(kpi_5_4_result);

   var kpi_table_5_5 = parseFloat($("#kpi_table_5_5").val());
   var kpi_table_5_6 = parseFloat($("#kpi_table_5_6").val());
   var kpi_table_5_7 = parseFloat($("#kpi_table_5_7").val());

   var kpi_table_4_5 = parseFloat($("#kpi_table_4_5").val());
   var kpi_table_4_6 = parseFloat($("#kpi_table_4_6").val());

   kpi_table_5_3 = parseFloat($("#kpi_table_5_3").val());
   kpi_table_4_5 = parseFloat($("#kpi_table_4_5").val());
   if (isNaN(kpi_table_4_5) || isNaN(kpi_table_5_3)) {
      $("#kpi_table_5_5").val("");
      return;
   }
   var kpi_5_5_result = (kpi_table_5_3 * kpi_table_4_5).toFixed(2);
   $("#kpi_table_5_5").val(kpi_5_5_result);

   kpi_table_5_3 = parseFloat($("#kpi_table_5_3").val());
   kpi_table_4_6 = parseFloat($("#kpi_table_4_6").val());
   if (isNaN(kpi_table_4_6) || isNaN(kpi_table_5_3)) {
      $("#kpi_table_5_6").val("");
      return;
   }
   var kpi_5_6_result = (kpi_table_5_3 * kpi_table_4_6).toFixed(2);
   $("#kpi_table_5_6").val(kpi_5_6_result);

   kpi_table_5_4 = parseFloat($("#kpi_table_5_4").val());
   kpi_table_5_5 = parseFloat($("#kpi_table_5_5").val());
   kpi_table_5_6 = parseFloat($("#kpi_table_5_6").val());
   if (isNaN(kpi_table_5_4) || isNaN(kpi_table_5_5) || isNaN(kpi_table_5_6)) {
      $("#kpi_table_5_7").val("");
      return;
   }
   var kpi_5_7_result = (kpi_table_5_4 + kpi_table_5_5 + kpi_table_5_6).toFixed(2);
   $("#kpi_table_5_7").val(kpi_5_7_result);

   var kpi_table_7_4 = parseFloat($("#kpi_table_7_4").val());
   var kpi_table_7_5 = parseFloat($("#kpi_table_7_5").val());
   var kpi_table_7_6 = parseFloat($("#kpi_table_7_6").val());
   if (isNaN(kpi_table_7_4) || isNaN(kpi_table_7_5) || isNaN(kpi_table_7_6)) {
      $("#kpi_table_7_7").val("");
      return;
   }
   var kpi_7_7_result = (kpi_table_7_4 + kpi_table_7_5 + kpi_table_7_6).toFixed(2);
   $("#kpi_table_7_7").val(kpi_7_7_result);

   var kpi_table_5_7 = parseFloat($("#kpi_table_5_7").val());
   var kpi_table_6_7 = parseFloat($("#kpi_table_6_7").val());
   if (isNaN(kpi_table_5_7) || isNaN(kpi_table_6_7)) {
      $("#kpi_table_8_7").val("");
      return;
   }
   var kpi_8_7_result = (kpi_table_5_7 * kpi_table_6_7).toFixed(2);
   $("#kpi_table_8_7").val(kpi_8_7_result);

   var kpi_table_7_4 = parseFloat($("#kpi_table_7_4").val());
   var kpi_table_8_7 = parseFloat($("#kpi_table_8_7").val());
   if (isNaN(kpi_table_7_4) || isNaN(kpi_table_8_7)) {
      $("#kpi_table_8_4").val("");
      return;
   }
   var kpi_8_4_result = (kpi_table_7_4 * kpi_table_8_7).toFixed(2);
   $("#kpi_table_8_4").val(kpi_8_4_result);

   var kpi_table_7_5 = parseFloat($("#kpi_table_7_5").val());
   var kpi_table_8_7 = parseFloat($("#kpi_table_8_7").val());
   if (isNaN(kpi_table_7_5) || isNaN(kpi_table_8_7)) {
      $("#kpi_table_8_5").val("");
      return;
   }
   var kpi_8_5_result = (kpi_table_7_5 * kpi_table_8_7).toFixed(2);
   $("#kpi_table_8_5").val(kpi_8_5_result);

   var kpi_table_7_6 = parseFloat($("#kpi_table_7_6").val());
   var kpi_table_8_7 = parseFloat($("#kpi_table_8_7").val());
   if (isNaN(kpi_table_7_6) || isNaN(kpi_table_8_7)) {
      $("#kpi_table_8_6").val("");
      return;
   }
   var kpi_8_6_result = (kpi_table_7_6 * kpi_table_8_7).toFixed(2);
   $("#kpi_table_8_6").val(kpi_8_6_result);

   var kpi_table_9_4 = parseFloat($("#kpi_table_9_4").val());
   var kpi_table_8_4 = parseFloat($("#kpi_table_8_4").val());
   if (isNaN(kpi_table_9_4) || isNaN(kpi_table_8_4)) {
      $("#kpi_table_10_4").val("");
      return;
   }
   var kpi_10_4_result = (kpi_table_9_4 * kpi_table_8_4).toFixed(2);
   $("#kpi_table_10_4").val(kpi_10_4_result);

   var kpi_table_9_5 = parseFloat($("#kpi_table_9_5").val());
   var kpi_table_8_5 = parseFloat($("#kpi_table_8_5").val());
   if (isNaN(kpi_table_9_5) || isNaN(kpi_table_8_5)) {
      $("#kpi_table_10_5").val("");
      return;
   }
   var kpi_10_5_result = (kpi_table_9_5 * kpi_table_8_5).toFixed(2);
   $("#kpi_table_10_5").val(kpi_10_5_result);

   var kpi_table_9_6 = parseFloat($("#kpi_table_9_6").val());
   var kpi_table_8_6 = parseFloat($("#kpi_table_8_6").val());
   if (isNaN(kpi_table_9_6) || isNaN(kpi_table_8_6)) {
      $("#kpi_table_10_6").val("");
      return;
   }
   var kpi_10_6_result = (kpi_table_9_6 * kpi_table_8_6).toFixed(2);
   $("#kpi_table_10_6").val(kpi_10_6_result);

   var kpi_table_10_4 = parseFloat($("#kpi_table_10_4").val());
   var kpi_table_10_5 = parseFloat($("#kpi_table_10_5").val());
   var kpi_table_10_6 = parseFloat($("#kpi_table_10_6").val());
   if (isNaN(kpi_table_10_4) || isNaN(kpi_table_10_5) || isNaN(kpi_table_10_6)) {
      $("#kpi_table_10_7").val("");
      return;
   }
   var kpi_10_7_result = (kpi_table_10_4 + kpi_table_10_5 + kpi_table_10_6).toFixed(2);
   $("#kpi_table_10_7").val(kpi_10_7_result);

   var kpi_table_8_7 = parseFloat($("#kpi_table_8_7").val());
   var kpi_table_10_7 = parseFloat($("#kpi_table_10_7").val());
   if (isNaN(kpi_table_8_7) || isNaN(kpi_table_10_7)) {
      $("#kpi_table_9_7").val("");
      return;
   }
   var kpi_9_7_result = (kpi_table_8_7 / kpi_table_10_7).toFixed(2);
   $("#kpi_table_9_7").val(kpi_9_7_result);

   var kpi_table_10_4 = parseFloat($("#kpi_table_10_4").val());
   var kpi_table_5_4 = parseFloat($("#kpi_table_5_4").val());
   if (isNaN(kpi_table_10_4) || isNaN(kpi_table_5_4)) {
      $("#kpi_table_11_4").val("");
      return;
   }
   var kpi_11_4_result = (kpi_table_10_4 / kpi_table_5_4).toFixed(2);
   $("#kpi_table_11_4").val(kpi_11_4_result);

   var kpi_table_10_5 = parseFloat($("#kpi_table_10_5").val());
   var kpi_table_5_5 = parseFloat($("#kpi_table_5_5").val());
   if (isNaN(kpi_table_10_5) || isNaN(kpi_table_5_5)) {
      $("#kpi_table_11_5").val("");
      return;
   }
   var kpi_11_5_result = (kpi_table_10_5 / kpi_table_5_5).toFixed(2);
   $("#kpi_table_11_5").val(kpi_11_5_result);

   var kpi_table_10_6 = parseFloat($("#kpi_table_10_6").val());
   var kpi_table_5_6 = parseFloat($("#kpi_table_5_6").val());
   if (isNaN(kpi_table_10_6) || isNaN(kpi_table_5_6)) {
      $("#kpi_table_11_6").val("");
      return;
   }
   var kpi_11_6_result = (kpi_table_10_6 / kpi_table_5_6).toFixed(2);
   $("#kpi_table_11_6").val(kpi_11_6_result);

   var kpi_table_9_4 = parseFloat($("#kpi_table_9_4").val());
   if (isNaN(kpi_table_9_4)) {
      $("#kpi_table_12_4").val("");
      return;
   }
   var kpi_12_4_result = (1 - kpi_table_9_4).toFixed(2);
   $("#kpi_table_12_4").val(kpi_12_4_result);

   var kpi_table_9_5 = parseFloat($("#kpi_table_9_5").val());
   if (isNaN(kpi_table_9_5)) {
      $("#kpi_table_12_5").val("");
      return;
   }
   var kpi_12_5_result = (1 - kpi_table_9_5).toFixed(2);
   $("#kpi_table_12_5").val(kpi_12_5_result);

   var kpi_table_9_6 = parseFloat($("#kpi_table_9_6").val());
   if (isNaN(kpi_table_9_6)) {
      $("#kpi_table_12_6").val("");
      return;
   }
   var kpi_12_6_result = (1 - kpi_table_9_6).toFixed(2);
   $("#kpi_table_12_6").val(kpi_12_6_result);

   var kpi_table_12_4 = parseFloat($("#kpi_table_12_4").val());
   var kpi_table_8_4 = parseFloat($("#kpi_table_8_4").val());
   if (isNaN(kpi_table_12_4) || isNaN(kpi_table_8_4)) {
      $("#kpi_table_13_4").val("");
      return;
   }
   var kpi_13_4_result = (kpi_table_12_4 * kpi_table_8_4).toFixed(2);
   $("#kpi_table_13_4").val(kpi_13_4_result);

   var kpi_table_12_5 = parseFloat($("#kpi_table_12_5").val());
   var kpi_table_8_5 = parseFloat($("#kpi_table_8_5").val());
   if (isNaN(kpi_table_12_5) || isNaN(kpi_table_8_5)) {
      $("#kpi_table_13_5").val("");
      return;
   }
   var kpi_13_5_result = (kpi_table_12_5 * kpi_table_8_5).toFixed(2);
   $("#kpi_table_13_5").val(kpi_13_5_result);

   var kpi_table_12_6 = parseFloat($("#kpi_table_12_6").val());
   var kpi_table_8_6 = parseFloat($("#kpi_table_8_6").val());
   if (isNaN(kpi_table_12_6) || isNaN(kpi_table_8_6)) {
      $("#kpi_table_13_6").val("");
      return;
   }
   var kpi_13_6_result = (kpi_table_12_6 * kpi_table_8_6).toFixed(2);
   $("#kpi_table_13_6").val(kpi_13_6_result);

   var kpi_table_13_4 = parseFloat($("#kpi_table_13_4").val());
   var kpi_table_13_5 = parseFloat($("#kpi_table_13_5").val());
   var kpi_table_13_6 = parseFloat($("#kpi_table_13_6").val());
   if (isNaN(kpi_table_13_4) || isNaN(kpi_table_13_5) || isNaN(kpi_table_13_6)) {
      $("#kpi_table_13_7").val("");
      return;
   }
   var kpi_13_7_result = (kpi_table_13_4 + kpi_table_13_5 + kpi_table_13_6).toFixed(2);
   $("#kpi_table_13_7").val(kpi_13_7_result);

   var kpi_table_13_7 = parseFloat($("#kpi_table_13_7").val());
   var kpi_table_8_7 = parseFloat($("#kpi_table_8_7").val());
   if (isNaN(kpi_table_13_7) || isNaN(kpi_table_8_7)) {
      $("#kpi_table_13_7").val("");
      return;
   }
   var kpi_12_7_result = (kpi_table_13_7 / kpi_table_8_7).toFixed(2);
   $("#kpi_table_12_7").val(kpi_12_7_result);


   var kpi_table_14_3 = parseFloat($("#kpi_table_14_3").val());
   if (isNaN(kpi_table_14_3)){
      $("#kpi_table_14_4").val("");
      $("#kpi_table_14_5").val("");
      $("#kpi_table_14_6").val("");
      return;
   }
   $("#kpi_table_14_4").val(kpi_table_14_3);
   $("#kpi_table_14_5").val(kpi_table_14_3);
   $("#kpi_table_14_6").val(kpi_table_14_3);

   var kpi_table_14_4 = parseFloat($("#kpi_table_14_4").val());
   var kpi_table_8_4 = parseFloat($("#kpi_table_8_4").val());
   if (isNaN(kpi_table_14_4) || isNaN(kpi_table_8_4)) {
      $("#csf_table_1_4").val("");
      return;
   }
   var csf_1_4_result = (kpi_table_8_4 / kpi_table_14_4).toFixed(4);
   $("#csf_table_1_4").val(csf_1_4_result);

   var kpi_table_14_5 = parseFloat($("#kpi_table_14_5").val());
   var kpi_table_8_5 = parseFloat($("#kpi_table_8_5").val());
   if (isNaN(kpi_table_14_5) || isNaN(kpi_table_8_5)) {
      $("#csf_table_1_5").val("");
      return;
   }
   var csf_1_5_result = (kpi_table_8_5 / kpi_table_14_5).toFixed(4);
   $("#csf_table_1_5").val(csf_1_5_result);

   var kpi_table_14_6 = parseFloat($("#kpi_table_14_6").val());
   var kpi_table_8_6 = parseFloat($("#kpi_table_8_6").val());
   if (isNaN(kpi_table_14_6) || isNaN(kpi_table_8_6)) {
      $("#csf_table_1_6").val("");
      return;
   }
   var csf_1_6_result = (kpi_table_8_6 / kpi_table_14_6).toFixed(4);
   $("#csf_table_1_6").val(csf_1_6_result);

   var kpi_table_14_4 = parseFloat($("#kpi_table_14_4").val());
   var kpi_table_14_5 = parseFloat($("#kpi_table_14_5").val());
   var kpi_table_14_6 = parseFloat($("#kpi_table_14_6").val());
   var kpi_table_8_7 = parseFloat($("#kpi_table_8_7").val());
   if (isNaN(kpi_table_14_4) || isNaN(kpi_table_14_5) || isNaN(kpi_table_14_6) || isNaN(kpi_table_8_7)) {
      $("#kpi_table_1_7").val("");
      return;
   }
   var csf_1_7_result = (kpi_table_8_7 / (kpi_table_14_4 + kpi_table_14_5 + kpi_table_14_6)).toFixed(4);
   $("#csf_table_1_7").val(csf_1_7_result);
}