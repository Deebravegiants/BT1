### Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers to route and label the event to the host application. Because those header fields are not part of the signed data, an attacker who can obtain any one genuinely-signed `(raw_body, hmac)` pair from Shopify (e.g., by installing the app on an attacker-controlled shop and receiving a real webhook for that shop) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` (and/or `topic`) header. The HMAC check still passes because it never looked at those headers, and the host application's handler will receive a `WebhookMetadata` claiming the event belongs to a different (victim) shop.

### Finding Description
The equality that should hold is:
`bytes verified by HmacValidator == bytes the application uses to identify the tenant (shop) and event type (topic)`

Instead:
- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) .
- `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from HTTP headers, completely independent of the HMAC-covered bytes [2](#0-1) .
- `HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (i.e., the raw body) and compares it to the `hmac-sha256` header, never touching `shop`, `topic`, or `webhook_id` [3](#0-2) .
- `Registry.process` gates everything on this single HMAC check, then immediately builds and dispatches `WebhookMetadata` using the unauthenticated `request.topic` and `request.shop` values, with no additional check that they correspond to the shop/topic the body was actually generated for [4](#0-3) .

Because the HMAC is computed only from `secret + raw_body` [5](#0-4) , any given `(raw_body, hmac)` pair remains valid regardless of which `shop-domain`/`topic` headers accompany it. Any actor able to receive one legitimate webhook for a shop they control (a completely normal, unprivileged action — installing the app and triggering an event) obtains a `(raw_body, hmac)` pair they can freely replay with a forged `shop-domain` header pointing at any other shop known to have installed the app, and `Registry.process` will accept it as if it came from that other shop.

### Impact Explanation
This breaks the tenant boundary the host application relies on: `Registry.process` hands the handler a `WebhookMetadata.shop` value that is attacker-controlled but presented as HMAC-verified, letting an attacker cause the app to process/attribute data to a shop (tenant) other than their own — a cross-tenant confusion. Depending on how the host application's handler trusts `data.shop` (e.g., to look up which merchant's session/store to update), this can result in cross-tenant data corruption, or an attacker triggering handler logic under the identity of a victim shop, even though they never obtained that shop's credentials.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on an attacker-controlled/free development shop to receive one legitimately HMAC-signed webhook (trivial, unprivileged, no credentials needed beyond a normal shop install), and (2) replaying the exact same raw body/HMAC to the app's public webhook endpoint with a modified `shop-domain` (and optionally `topic`) header. No access to `api_secret_key`, access tokens, or the victim's credentials is required, and the request goes to a publicly reachable endpoint. This is realistically exploitable by any developer/merchant who can install the target app.

### Recommendation
Bind the identity fields to the signed payload before trusting them: either (a) include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (`to_signable_string`) so tampering invalidates the signature, or (b) have `Registry.process` cross-check `request.shop`/`request.topic` against values embedded in the verified JSON body (Shopify webhook payloads typically include shop/topic-identifying fields) rather than relying purely on headers that sit outside the HMAC boundary.

### Proof of Concept
1. Install the app on an attacker-owned development shop `attacker.myshopify.com`; trigger a webhook event (e.g., `orders/create`) and capture the resulting HTTP request, including the raw body and the valid `x-shopify-hmac-sha256` header value that Shopify computed with the app's shared secret.
2. Replay this exact request to the app's webhook endpoint, but replace the `x-shopify-shop-domain` header with `victim-shop.myshopify.com` (and, if desired, change `x-shopify-topic` to a topic with a registered handler in the app).
3. Call the flow the same way the host app does:
```ruby
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: {
    "x-shopify-hmac-sha256" => captured_valid_hmac,
    "x-shopify-topic" => "orders/create",
    "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  })
)
```
4. `HmacValidator.validate` succeeds because it only checks `raw_body` against the secret [6](#0-5) , and `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` [7](#0-6)  — even though that shop never sent this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
