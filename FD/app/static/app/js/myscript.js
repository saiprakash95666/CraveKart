$(document).on('click', '.plus-cart', function(){
    var id = $(this).attr("pid").toString();
    var element = this.parentNode.children[2];
    $.ajax({
        type: 'GET',
        url: '/pluscart',
        data: {
            prod_id: id
        },
        success: function(data){
            element.innerText = data.quantity;
            document.getElementById("amount").innerText = data.amount;
            document.getElementById("totalamount").innerText = data.totalamount;
        }
    });
});

$(document).on('click', '.minus-cart', function(){
    var id = $(this).attr("pid").toString();
    var element = this.parentNode.children[2];
    $.ajax({
        type: 'GET',
        url: '/minuscart',
        data: {
            prod_id: id
        },
        success: function(data){
            element.innerText = data.quantity;
            document.getElementById("amount").innerText = data.amount;
            document.getElementById("totalamount").innerText = data.totalamount;
        }
    });
});

$(document).on('click', '.remove-cart', function(){
    var id = $(this).attr("pid").toString();
    var element = $(this);
    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: {
            prod_id: id
        },
        success: function(data){
            document.getElementById("amount").innerText = data.amount;
            document.getElementById("totalamount").innerText = data.totalamount;
            element.closest('.cart-item').remove();

            if (data.cart_empty) {
                $('.cart-wrapper').html('<h3 class="text-center">Your cart is empty.</h3>');
            }
        }
    });
});
