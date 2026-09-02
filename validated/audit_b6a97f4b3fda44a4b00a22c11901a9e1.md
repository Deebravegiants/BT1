Based on my analysis, I've confirmed the strongest analog in this gem.

### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
The reported bug class is: a guard/validator makes a trust decision using a field that is not actually protected by the security check it relies on (the `pool::occupied_ticks` counter is checked but not correctly tied to the state it's meant to gate). The analogous flaw here is an identity-binding break where the HMAC signature validated on inbound Shopify webhooks does not cover the `shop-domain` field that the app uses to attribute and process the webhook, i.e. bytes verified ≠ bytes that determine tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts the shop identity from the `X-Shopify-Shop-Domain` header via `shop`, but its `to_signable_string` — the data that `Utils::HmacValidator` actually verifies — is only the raw request body: [1](#0-0) 

`Utils::HmacValidator.validate` computes an HMAC over `to_signable_string` (the body) using the app's single, shop-agnostic `api_secret_key` and compares it to the `hmac-sha256` header: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching the handler with `shop: request.shop` taken straight from the (unsigned) header: [3](#0-2) 

The identity binding the code relies on is: `HMAC-verified(body) == authenticated(shop)`. In reality the equality only holds for `HMAC-verified(body)`; `shop` is parsed from a header that participates in neither the signature computation nor any subsequent validation (no comparison against a shop stored with the delivery, no per-shop secret). Because the same `api_secret_key` signs webhooks for every shop that installs the app, a valid `(body, hmac)` pair captured from one shop's webhook delivery remains valid for any other value the attacker puts in the `shop-domain` header.

### Impact Explanation
An unprivileged internet user who controls a shop that has legitimately installed the app (a routine, unprivileged action — no special credentials needed beyond installing a public app) can capture one of their own genuine, HMAC-valid webhook deliveries and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop. The HMAC still validates (it never covered the header), so `Registry.process` dispatches the handler believing the payload originated from the victim shop. This is a cross-tenant identity confusion: the app will act on/store data under the wrong shop's context (e.g. process `orders/create`, `app/uninstalled`, `shop/redact`, or `customers/data_request` payloads as if from the victim), which can lead to tenant data corruption, unauthorized triggering of shop-scoped app logic, or bypass of shop-specific processing rules — squarely matching the "cross-tenant access" impact category.

### Likelihood Explanation
The attacker only needs the ability any developer/merchant has: install the public app on their own store to receive genuine webhook deliveries. No secret key, session, or access token theft is required, and no host-application misuse is involved — the gem's own `Request`/`Registry`/`HmacValidator` classes are used exactly as documented. This makes the likelihood high for any app that trusts `WebhookMetadata#shop` (populated from `request.shop`) for shop-scoped logic.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header bytes in the HMAC-signed material verified by `Utils::HmacValidator`, or otherwise cryptographically bind the shop domain to the signature (e.g., verify the shop is one with an active session/registration known to the app before dispatch) so that `to_signable_string` in `lib/shopify_api/webhooks/request.rb` cannot be replayed under a different tenant identity.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged action).
2. Shopify sends a legitimate webhook, e.g. `orders/create`, to the app's endpoint with body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and `X-Shopify-Hmac-Sha256: H = base64(HMAC-SHA256(api_secret_key, B))`.
3. Attacker captures `(B, H)` from their own delivery (e.g., via a logging proxy they control since it's their own installed app instance).
4. Attacker sends a forged HTTP request directly to the app's public webhook endpoint with the same body `B` and same `H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses headers, `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only — matches `H` — validation passes at [4](#0-3) .
6. `Registry.process` calls the handler with `WebhookMetadata.new(..., shop: request.shop, ...)` where `request.shop` returns `"victim-shop.myshopify.com"`, causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
