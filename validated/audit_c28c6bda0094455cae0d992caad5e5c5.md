Confirmed root cause. The webhook HMAC in `Utils::HmacValidator.validate` only signs `Request#to_signable_string`, which returns the raw JSON body [1](#0-0) , while `Registry.process` extracts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` directly from unauthenticated HTTP headers and hands them straight to the app's `WebhookHandler#handle` as trusted tenant/metadata fields [2](#0-1) [3](#0-2) . Since the app's `api_secret_key` is shared across *all* merchant shops using the app, any unprivileged person can install the app on their own free/dev store, receive a legitimately-signed webhook body+HMAC for content they control, and replay that exact body/HMAC to the app's public webhook endpoint while swapping the `shopify-shop-domain` (and other) headers to point at a victim shop. `HmacValidator.validate` still passes because it never inspects the shop header [4](#0-3) , so the host app processes attacker-controlled data as if it came from the victim tenant.

### Title
Webhook HMAC does not bind the `shop` (tenant) header, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so the HMAC computed by `Utils::HmacValidator` never covers the `X-Shopify-Shop-Domain` header (or the topic/webhook-id/api-version headers). `Registry.process` trusts these headers verbatim and passes them to the app's registered `WebhookHandler` as the authenticated shop/tenant identity.

### Finding Description
The equality that should hold is: *shop identity authenticated by the HMAC == shop identity acted upon by the handler*. In this gem:
- `Request#hmac` reads `shopify-hmac-sha256` and `to_signable_string` returns `@raw_body` only [5](#0-4) .
- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are read straight from headers with no cryptographic binding to the body or HMAC [6](#0-5) .
- `HmacValidator.validate` verifies only `verifiable_query.to_signable_string` against `verifiable_query.hmac` — i.e., body vs. body-HMAC, never shop vs. anything [7](#0-6) .
- `Registry.process` raises only if the HMAC over the body fails, then immediately builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` and dispatches it to the host app's handler as trusted data [2](#0-1) [3](#0-2) .

Because Shopify apps use a single `api_secret_key` shared across every merchant/shop that installs the app (this is inherent to the OAuth model this gem implements — see `Context.api_secret_key` used identically for all shops in `Auth::Oauth`/`HmacValidator`), any unprivileged person can:
1. Create their own free/dev Shopify store and install the target app (no privileged credentials needed — this is the normal, unauthenticated app-install flow).
2. Trigger a webhook topic with content they control (e.g. by editing an order/product on their own store), receiving a validly HMAC-signed body from Shopify for their own shop.
3. Capture that raw body + `X-Shopify-Hmac-Sha256` value.
4. Replay the identical body and HMAC to the target app's public webhook endpoint, but substitute `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) with the victim shop's domain.
5. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches attacker-chosen `body` to the host app's handler as if Shopify itself certified that this data came from the victim shop.

This breaks the intended binding "the shop header is only trustworthy because the HMAC proves Shopify sent it for that shop" — the HMAC proves nothing about which shop sent it.

### Impact Explanation
This crosses a tenant boundary: an app that uses `WebhookMetadata#shop` to identify which merchant's session/data to update (a extremely common and expected use pattern, since that's the entire purpose of exposing `shop` on the struct) can be made to apply attacker-controlled webhook payloads to another merchant's tenant record — e.g., forcing bogus `app/uninstalled`, `shop/redact`, `orders/create`, or inventory/fulfillment updates to fire against a victim shop's data, corrupting or exfiltrating cross-tenant state. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High/practical: no special privileges, leaked secrets, or victim shop credentials are required. Any person can self-register a shop, install the target app for free, and capture one legitimately-signed webhook to reuse against any other shop simply by swapping an unauthenticated header. The only per-app constant needed (`api_secret_key`) is never exposed to the attacker because they don't need it — they get a valid signature "for free" from their own installation.

### Recommendation
Bind the shop (and topic/webhook id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the specific installation/session before trusting it in `WebhookMetadata`. Concretely:
- Change `Request#to_signable_string` to include the shop domain (and topic) in the signed payload, or
- After HMAC validation, cross-check `request.shop` against an independently-verified value (e.g., look up the session/access token for that shop and verify it actually has an active webhook subscription id matching `request.webhook_id`), rejecting the webhook if it doesn't match, and
- Document clearly for consumers of `Registry.process`/`WebhookHandler#handle` that `data.shop` is not itself authenticated by the HMAC and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. Attacker creates a free Shopify partner/dev store `attacker.myshopify.com` and installs the target app (normal, unauthenticated OAuth install flow using the app's public `client_id`).
2. Attacker triggers a subscribed webhook topic (e.g. `products/update`) on `attacker.myshopify.com` with a payload of their choosing, and captures the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H` sent by Shopify (H is a valid HMAC-SHA256 of `B` under the app's `api_secret_key`, per `Request#hmac`/`to_signable_string` at `lib/shopify_api/webhooks/request.rb:10-38`).
3. Attacker sends a new POST to the app's public webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` (`lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and invokes the host app's `handle(data:)` with attacker-controlled `body` attributed to the victim shop, despite Shopify never having sent this content for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
