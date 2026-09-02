### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then hands the `shop` value taken from an **unsigned** HTTP header to the app's webhook handler. Because the `shop-domain` header is never included in the HMAC-signed content, an attacker who possesses one valid `(body, hmac)` pair (trivially obtainable by installing the app on their own store and triggering a webhook) can replay that exact body/HMAC while substituting an arbitrary `shop-domain` header value, causing the app to process the payload as if it belonged to a different (victim) shop.

### Finding Description
The webhook signature check is implemented generically via `Utils::VerifiableQuery`/`Utils::HmacValidator`: [1](#0-0) 

For webhooks, the signable content is defined as only the raw body: [2](#0-1) 

Meanwhile the `shop` accessor comes straight from an HTTP header that is never part of that signed string: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` — the unauthenticated header — to the application's handler as the tenant identifier for the event: [4](#0-3) 

This breaks the intended binding: `HMAC(body) == valid` is supposed to imply `shop == the shop that generated this webhook`, i.e. `verified_bytes == acted_upon_shop`. In reality the equality only holds for `body`; `shop`, `topic`, `api_version`, and `webhook_id` are all attacker-controlled headers that ride along unauthenticated. Any party who can get one legitimately signed `(body, hmac)` pair — for example by installing the app on their own store, since installing an app and receiving its own webhooks requires no privileged Shopify credentials — can resend that same body/HMAC to the app's webhook endpoint while swapping in an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header naming any other merchant. The library will accept it as authentic (HMAC validates) and dispatch it to the handler tagged with the attacker-chosen `shop`.

### Impact Explanation
This is a cross-tenant boundary break: the gem asserts a webhook event is authentic for tenant X purely because the *body* bytes are HMAC-valid, while the actual tenant identity delivered to the host application's handler is taken from unauthenticated header bytes. Any host application that uses `WebhookMetadata#shop` to select which merchant record to update (the documented, expected usage) can be made to write/mutate/act on data belonging to an arbitrary shop using attacker-controlled webhook content, i.e., a cross-tenant access primitive fully within the scope of "identity binding broken."

### Likelihood Explanation
Likelihood is high for any unprivileged internet user: obtaining one valid signed webhook only requires installing the target app on a shop the attacker controls (a normal, unprivileged action any developer/merchant can do) and capturing a triggered webhook request. No access token, `client_secret`, or leaked credential of the victim is required — only the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with headers of the attacker's choosing, which is inherent to how HTTP webhook receivers work.

### Recommendation
Include the tenant-identifying headers (`shop`, `topic`, `api_version`, `webhook_id`) in the signable content used by `HmacValidator`, or otherwise cryptographically bind the `shop-domain` header to the signed payload (e.g., derive/verify it from a signed claim rather than trusting the raw header) before it is handed to `WebhookMetadata`/the application handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers an event (e.g., `orders/create`) to receive a legitimately signed webhook with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC(api_secret_key, B)`.
2. Attacker resends the exact same request to the app's public webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but replaces `x-shopify-shop-domain: attacker-shop.myshopify.com` with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers (only checks for their *presence*, not their integrity) — [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(body)` — [6](#0-5) .
5. The handler receives `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)` and processes/act on it as if it were a legitimate event from `victim-shop`, despite `victim-shop` never having sent anything.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
