### Title
Webhook HMAC signs only the raw body, so `shop`, `topic`, `webhook_id`, and `api_version` are unauthenticated and can be swapped to spoof the tenant a webhook is attributed to - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string [2](#0-1) . Meanwhile, `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all read directly from HTTP headers with no cryptographic binding to the signed body [3](#0-2) . `Registry.process` validates the HMAC and then trusts these header-derived fields to build the `WebhookMetadata` handed to the app's handler, using `request.shop` as the tenant identity and `request.topic` to select the handler [4](#0-3) . This is the same bug class as the report: the check (HMAC over `raw_body`) is validated, but a different, unguarded field (`shop`/`topic`/`webhook_id`/`api_version` headers) is what actually gets acted upon.

### Finding Description
The equality this gem is supposed to guarantee is:
`bytes verified by HMAC == bytes/identity acted upon by the handler`

Here that equality is broken:
- Bytes verified: `@raw_body` only, via `OpenSSL.secure_compare(computed_signature, received_signature)` where `computed_signature = HMAC(secret, raw_body)` [5](#0-4) .
- Bytes/identity acted upon: `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id)` [6](#0-5) , where `topic`, `shop`, `api_version`, `webhook_id` are unauthenticated HTTP headers [3](#0-2) .

Because `shop` is not part of the signed payload, once an attacker is in possession of any single legitimately-signed `(raw_body, hmac)` pair — trivially obtainable by installing the same public app on the attacker's own development/test store and capturing one real webhook delivery — the attacker can replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) with a victim shop's domain. `HmacValidator.validate` will still pass, because it only checks `raw_body` against the signature, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop [4](#0-3) . No knowledge of `api_secret_key` is required for this replay — the attacker only needs one prior valid signature obtained through their own legitimate installation, which they can always get from Shopify by triggering an event (e.g. `app/uninstalled`) on their own dev store.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` as the tenant key to look up/update per-merchant state (a well-documented and expected pattern, since that's the field's entire purpose per `docs/usage/webhooks.md`), this allows cross-tenant data corruption/injection: an attacker can cause the app to process a webhook body as if it belonged to an arbitrary victim shop, e.g. forcing an `app/uninstalled` handler to wipe or deactivate a victim's stored session/data, or injecting attacker-controlled body content attributed to the victim tenant. This matches the "cross-tenant access" impact category, since the gem itself provides no way for the host app to distinguish a genuine webhook for shop A from a replayed one falsely labeled as shop B.

### Likelihood Explanation
High for any consumer relying on the gem's own `Registry.process`/`WebhookMetadata` contract as documented: the only precondition is possession of one valid `(body, hmac)` pair, which any developer/attacker can obtain for free by installing the target app (or any app using this library with the same secret model) on their own store and capturing a real webhook delivery. No access token, `client_secret`, or privileged access to the victim's account is needed.

### Recommendation
Include the tenant-identifying and routing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification (or otherwise cryptographically bind them to the body before dispatch), so that `HmacValidator.validate` fails if any of these headers are altered relative to what Shopify actually signed. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are not authenticated by the HMAC and must not be used as a sole tenant/routing identifier without additional verification (e.g., cross-checking against a shop already known to have subscribed to that specific `webhook_id`).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook event (e.g. uninstalls the app to fire `app/uninstalled`), capturing the real request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for secret `S`).
2. Attacker replays the exact same body `B` and header `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)` [7](#0-6) ; validation passes because `to_signable_string` returns only `B`, unaffected by the header change [1](#0-0) .
4. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim.myshopify.com", topic: ..., body: parsed(B), ...)` [6](#0-5) , causing the app to act on victim's tenant data using attacker-supplied body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

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
