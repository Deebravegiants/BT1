### Title
Webhook `shop`, `topic`, and `webhook_id` headers are trusted but not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then dispatches to the registered handler using `topic` and `shop` values pulled straight from unauthenticated HTTP headers. Because the signature never covers those headers, any party who can obtain one valid `(body, hmac)` pair for the app's shared `client_secret` — trivially available to any merchant who installs the app on their own store and receives a legitimate webhook — can replay that exact body/hmac pair to the app's public webhook endpoint while swapping the `shop-domain`, `topic`, and `webhook-id` headers to arbitrary values. The signature check still passes because it only re-computes the HMAC over `@raw_body`.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `HMAC(secret, verifiable_query.to_signable_string)`. [1](#0-0) 

For webhook requests, `to_signable_string` returns only `@raw_body`, and none of `topic`, `shop`, `webhook_id`, or `api_version` are folded into the signable string — they are read directly from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` only checks the body HMAC, then trusts `request.topic` to select the handler and passes `request.shop` (an unauthenticated header) straight into `WebhookMetadata` for the handler to act on: [3](#0-2) 

The identity binding that should hold is:
`HMAC_valid(raw_body) == true` should imply `shop header == the shop that actually generated raw_body` and `topic header == the topic Shopify actually fired`.

That binding does not hold here, because the signature is computed only over `raw_body` with the app's single shared `api_secret_key` (the same secret is used for every shop that installs the app). Any merchant — including a free/dev-store attacker — can install the app on their own shop, trigger a real event, capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair that Shopify legitimately sent them, and then POST that same body/hmac pair to the app's webhook endpoint with a forged `x-shopify-shop-domain` (pointing at a victim shop) and/or a forged `x-shopify-topic` (pointing at a different, more sensitive registered topic, e.g. `app/uninstalled`, `customers/redact`, `shop/update`). `Registry.process` will accept the request as authentic and invoke the host application's handler with attacker-chosen `shop` and `topic` values, since only body integrity — not header-to-body binding — is checked.

### Impact Explanation
This crosses a tenant boundary: the gem's own webhook dispatch attests requests as coming from a specific shop/topic purely from unauthenticated headers, letting one merchant's app forge webhook deliveries that host applications will process as if they originated from a different merchant/shop or a different topic. Since host apps built on this library are expected to trust `WebhookMetadata#shop` (it's the field the library itself hands to the handler as the authenticated tenant identifier), this enables cross-tenant data corruption/access in the host application, satisfying the "cross-tenant access" high/critical impact bar.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate merchant of the target app (or any low-privilege actor who can trigger at least one real webhook delivery for the app, e.g., via a free trial/dev store) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is required beyond what any app installer already has.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook-id` headers in the HMAC-signed material (or otherwise cryptographically bind them to the body) before computing/verifying the signature in `Request#to_signable_string`/`HmacValidator`, so a mismatch between the claimed headers and the originally signed request is rejected. At minimum, document and/or enforce that host applications must not treat `WebhookMetadata#shop` as authenticated unless it is independently corroborated (e.g., cross-checked against the delivery's registered destination), and consider deriving the shop from a value that is actually part of the signed payload where Shopify's webhook payload includes it.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets Shopify deliver a real webhook, capturing `raw_body` and the `x-shopify-hmac-sha256` header — both signed with the app's shared `api_secret_key`.
2. Attacker POSTs the identical `raw_body` to the app's webhook endpoint but rewrites headers:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic: app/uninstalled` (or any other topic the app has registered)
3. `ShopifyAPI::Webhooks::Request.new` accepts these headers unchanged. [4](#0-3) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only, ignoring the forged headers, and passes. [5](#0-4) 
5. The registered handler for `app/uninstalled` (or whichever topic was forged) is invoked with `shop: "victim.myshopify.com"`, causing the host app to act on the victim shop's tenant data as if Shopify had genuinely sent that event for that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
