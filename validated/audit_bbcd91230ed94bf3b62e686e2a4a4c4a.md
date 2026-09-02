## Title
Webhook shop/topic identity spoofing via unauthenticated headers not covered by the HMAC — cross-tenant webhook confusion (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

## Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body [1](#0-0) . However, the `shop` (and `topic`) values that are subsequently trusted and handed to the app's handler come from HTTP headers that are **not** included in the HMAC-signed payload [2](#0-1) . Because the same `api_secret_key` is shared across every shop that has installed a given app, this breaks the intended binding `shop-domain header == originating shop of raw_body`, allowing a legitimately-installed (but malicious) shop to relabel their own genuinely-signed webhook payload as belonging to a different, victim shop.

## Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `Utils::HmacValidator.validate` computes/compares the HMAC purely against this signable string using `Context.api_secret_key` [4](#0-3) . The `shop`, `topic`, `webhook_id`, and `api_version` values are all read directly from HTTP headers with no cryptographic binding to the body [5](#0-4) .

`Registry.process` uses only `Utils::HmacValidator.validate(request)` as its authentication check, then dispatches to the app's handler using the unauthenticated `request.shop` and `request.topic` fields as truth: [6](#0-5) 

Since `api_secret_key` is the app's single client secret (shared across every merchant install, not a per-shop secret), any attacker who installs the app on their own shop can:
1. Trigger an event on their own shop to receive a legitimately Shopify-signed webhook (`raw_body` + valid `x-shopify-hmac-sha256`).
2. Replay that exact `raw_body`/HMAC pair directly to the app's public webhook endpoint, substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header with a victim shop's domain or a different topic.
3. `HmacValidator.validate` still succeeds because it only checks `raw_body` against the shared secret — the forged `shop`/`topic` headers are never verified.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, i.e., with attacker-controlled tenant/topic identity attached to a validly-signed but misattributed payload.

This precisely matches the "field acted on but not covered by the HMAC" analog class: the equality that should hold — `shop header used by handler == shop that actually produced/authorized raw_body` — is not enforced anywhere in the gem's webhook path.

## Impact Explanation
This enables cross-tenant confusion at the webhook-processing boundary: an app relying on `WebhookMetadata#shop` (as documented/intended, per `Registry.process`'s own usage) to determine which merchant's session/data to act on can be made to process an attacker's payload under a victim shop's identity, or misroute a payload to the wrong topic handler. Depending on how the host app uses `data.shop` (e.g., to look up/act on a stored session or merchant record), this can lead to unauthorized cross-tenant data writes/state changes performed against the wrong shop's context — satisfying the "cross-tenant access" criteria for Critical impact.

## Likelihood Explanation
Exploitability requires only: (a) being able to install the target app on an attacker-controlled shop (any developer/merchant can do this — no privileged credentials needed), and (b) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers (trivial, no bypass of TLS/interception needed since the attacker is a legitimate sender of their own webhook data, just re-targeted). No `api_secret_key`, access token, or leaked credential is required — the attacker only ever uses their own legitimately obtained webhook payload.

## Recommendation
Bind the `shop` (and ideally `topic`) values into the HMAC-verified data, or otherwise validate that the `shop-domain` header corresponds to a shop the receiving webhook endpoint/route is registered for (e.g., cross-check against the specific merchant session expected on that route) before trusting `request.shop` for any tenant-scoped action. At minimum, document that `WebhookMetadata#shop`/`#topic` are unauthenticated fields and must not be used as the sole tenant/topic identity for any privileged or data-mutating operation without additional server-side verification (e.g., per-shop registered callback path, or storing an expected mapping of webhook_id → shop returned at registration time).

## Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker-shop.myshopify.com"
# and triggers an event, capturing the legitimately-delivered webhook:
raw_body = '{"id": 1, "note": "hello"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_CLIENT_SECRET, raw_body)

# Attacker replays the SAME body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to the victim shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- forged, unverified
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate succeeds (body+secret match),
#    handler.handle is invoked with shop: "victim-shop.myshopify.com"
``` [6](#0-5) [2](#0-1)

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
