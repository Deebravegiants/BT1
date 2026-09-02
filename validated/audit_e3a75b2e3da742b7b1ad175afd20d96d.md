I have enough evidence to confirm the analog. Confirmed: `ShopifyAPI::Webhooks::Request#hmac` validates against `to_signable_string` which returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated headers [2](#0-1) . `Registry.process` only calls `Utils::HmacValidator.validate(request)` (which validates the body) before dispatching `request.shop` to the app's handler as the tenant identifier [3](#0-2) .

### Title
Webhook shop-domain header not bound to HMAC signature enables cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using an HMAC computed over the raw body only, but derives the tenant-identifying `shop` (and `topic`/`webhook_id`/`api_version`) fields from HTTP headers that are excluded from that signature. This breaks the identity binding: `hmac(raw_body) == valid` while `shop header ∈ signed bytes` is false.

### Finding Description
`Request#to_signable_string` returns just `@raw_body` [1](#0-0) . `Request#shop` reads `shopify-shop-domain`/`x-shopify-shop-domain` directly from attacker-controllable headers with no cross-check against the signed content [4](#0-3) . `HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and only compares against `verifiable_query.hmac` [5](#0-4) , so it never touches the shop-domain header. `Registry.process` gates only on this body HMAC and then forwards `request.shop` into `WebhookMetadata` for the app's handler to act on [3](#0-2) .

Because the same `api_secret_key` is shared across every shop installed on a given app, any tenant that legitimately receives a real webhook (with a valid body+HMAC pair for its own shop) can capture that pair and resend it to the app's webhook endpoint with the `shop-domain` header rewritten to a different, victim shop. The HMAC check still passes because it only covers the body bytes, which are unchanged. `Registry.process` will then treat the payload as originating from the victim shop and hand `shop: <victim-domain>` to the app's handler.

### Impact Explanation
This crosses the tenant boundary the gem is expected to enforce: an attacker who is a legitimate, unprivileged merchant on the app (no special credentials, no access token, no `api_secret_key` needed beyond what their own shop's genuine webhook already gives them) can make the host application ingest a webhook body under an arbitrary victim shop's identity. Depending on how the host app's handler uses `data.shop` (e.g., to select which merchant record to update, credit, or notify), this can lead to cross-tenant state corruption using data the attacker fully controls.

### Likelihood Explanation
Requires only capturing one legitimate webhook delivery to the attacker's own shop (trivial — attacker fully controls their own shop's webhook traffic and can trigger events like `orders/create` on demand) and replaying it with a modified header. No secrets, tokens, or privileged access are required beyond what an ordinary app-installing merchant already has.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., creates an order), capturing the raw POST body and the genuine `X-Shopify-Hmac-Sha256` header value Shopify computed over that body.
2. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` only and it matches, since the body is untouched [6](#0-5) .
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` [7](#0-6) , so the app processes attacker-supplied data under the victim shop's tenant identity.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the authenticated material — e.g., require the host app to independently verify that the `shop-domain` header corresponds to a shop with an active, known installation/session before trusting it, or extend `to_signable_string`/validation to incorporate a per-shop secret or the shop domain itself so header tampering invalidates the signature.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
