DEFAULT_TABLE_DESCRIPTIONS = """
Table Purposes and Context:

1. Fulfillment Table:
    - Purpose: Captures qualitative data for market research
    - Contains customer instructions and notes
    - Good for analyzing customer preferences and special requests

2. Orders Table:
    - Central hub for managing and recording customer orders
    - Tracks complete order lifecycle from placement to fulfillment
    - Enables descriptive analytics of transactions
    - Supports quantitative market research
    - Primary source for transaction analysis

3. Daily_Sales Table:
    - Provides daily business performance summaries
    - Consolidates data for operational snapshots
    - Supports forecasting and trend analysis
    - Enables quick report generation with reduced lag time
    - Lighter alternative to detailed transaction reports

4. Orders_Itemized Table:
    - Tracks individual line items within orders
    - Provides granular transaction details
    - Supports detailed product-level analysis
    - Ensures financial compliance and transparency
    - Enables precise reporting on product sales

5. Product_Sales Table:
    - Focuses on product-specific sales tracking
    - Records variants, quantities, and pricing
    - Supports product performance analytics
    - Enables trend analysis at product level
    - Tracks daily product revenue
"""

DEFAULT_TABLE_SCHEMA = """
Table: fulfillment
- item_instructions (text): Customer-provided notes for specific items
- order_notes (text): General order-related customer notes
- fulfillment_date (timestamp): When customer instructions were provided

Table: orders
- order_id (varchar): Primary key, unique order identifier
- order_time (timestamp): When order was placed
- subtotal (decimal): Pre-tax/fees order amount
- taxable_items (decimal): Amount for tax-eligible items
- non_taxable_items (decimal): Amount for tax-exempt items (bulk purchases)
- delivery_fee (decimal): Standard delivery charge
- tax (decimal): Total tax applied
- stripe_tendered (decimal, nullable): Online payment amount via Stripe
- total_payments_tendered (decimal): Total paid across all methods
- gift_cards_purchased (decimal): New gift card purchase value
- gift_cards_tendered (decimal): Payment via existing gift cards
- refunded (decimal): Total refund amount
- net_sales (decimal): Final amount after all adjustments
- items (text): Detailed item list with quantities
- fulfillment_method (varchar): PICKUP, DELIVERY, or Point of Sale
- fulfillment_time (timestamp): Pickup/delivery completion time
- city (varchar): Customer city (online orders)
- province (varchar): Customer province (online orders)
- postal_code (varchar): Customer postal code (online orders)

Table: daily_sales
- date (date): Primary key for daily summary
- orders_count (integer): Total daily orders
- delivery_fees_count (integer): Number of deliveries
- delivery_fees_amount (decimal): Total standard delivery fees
- priority_express_delivery (decimal): Total expedited delivery fees
- tax (decimal): Total daily tax collected
- stripe_tendered_online (decimal): Total online payments
- gift_cards_purchased (decimal): New gift card sales
- gift_cards_tendered (decimal): Gift card payments
- refunded (decimal): Total refunds
- net_sales (decimal): Final daily revenue

Table: orders_itemized
- order_id (varchar): References orders.order_id
- time_placed (timestamp): Item addition time
- item_category (varchar): Product, Add-on, Tax, Tips, Fulfillment
- item_name (varchar): Item description
- product_type (varchar): Product category
- product_variant (varchar, nullable): Product SKU
- quantity (integer): Number of units
- unit_price (decimal): Base price per unit
- subtotal (decimal): Pre-tax/fees amount
- delivery_fee (decimal): Item delivery charge
- tax (decimal): Item tax amount
- total (decimal): Total with tax and fees
- gift_card_purchased (decimal): Gift card value if applicable
- net_sales (decimal): Final item revenue
- fulfillment_method (varchar): Delivery or Pickup

Table: product_sales
- product (varchar): Product name
- variant (varchar): Product SKU
- sale_date (date): Sale date
- count (integer): Units sold
- unit_price (decimal): Price per unit
- subtotal (decimal): Total revenue
- tax (decimal): Tax collected

Key Relationships and Notes:
1. orders_itemized.order_id links to orders.order_id for detailed transaction lookup
2. daily_sales aggregates orders data by date for summary reporting
3. product_sales aggregates orders_itemized by product and date
4. fulfillment links to orders for customer instructions
5. Online orders (stripe_tendered not null) include customer location data
6. Bulk purchases (1/2 or 1 Dozen) are tax-exempt
"""


DEFAULT_TABLE_COLUMNS = {
    "gold.fulfillment": ["item_instructions", "order_notes", "fulfillment_date"],
    "gold.orders": [
        "order_id",
        "order_time",
        "subtotal",
        "taxable_items",
        "non_taxable_items",
        "delivery_fee",
        "tax",
        "stripe_tendered",
        "total_payments_tendered",
        "gift_cards_purchased",
        "gift_cards_tendered",
        "refunded",
        "net_sales",
        "items",
        "fulfillment_method",
        "fulfillment_time",
        "city",
        "province",
        "postal_code",
    ],
    "gold.daily_sales": [
        "date",
        "orders_count",
        "delivery_fees_count",
        "delivery_fees_amount",
        "priority_express_delivery",
        "tax",
        "stripe_tendered_online",
        "gift_cards_purchased",
        "gift_cards_tendered",
        "refunded",
        "net_sales",
    ],
    "gold.orders_itemized": [
        "order_id",
        "time_placed",
        "item_category",
        "item_name",
        "product_type",
        "product_variant",
        "quantity",
        "unit_price",
        "subtotal",
        "delivery_fee",
        "tax",
        "total",
        "gift_card_purchased",
        "net_sales",
        "fulfillment_method",
    ],
}
