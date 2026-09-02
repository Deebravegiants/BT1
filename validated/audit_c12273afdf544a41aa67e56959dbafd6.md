### Title
Webhook `shop` identity is read from an unauthenticated header and is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body, not this header. This is the same bug class as the CDP.sol report: a field that is acted upon (`shop`, used to identify the tenant) is not covered by the cryptographic check that is supposed to authenticate the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` value, however, comes straight from a header that is entirely attacker-controlled bytes on the wire, independent of the signed payload: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `to_signable_string` (the body) using the app's `client_secret`/`api_secret_key`, and only checks that value against the `hmac` header: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then, on success, hands `request.shop` straight to the app's handler as the trusted tenant identifier, with no further check that ties `shop` to the signed body: [4](#0-3) 

The identity binding that should hold is: `hmac == HMAC(secret, body)` implies `shop == tenant that produced body`. In reality the code only proves `hmac == HMAC(secret, body)`; the `shop` field is parsed but never authenticated. Because the HMAC secret is the single app-wide `client_secret`/`api_secret_key` (shared across every shop that has the app installed), *any* merchant who has the app installed can receive a legitimately-signed webhook for their own store (valid `hmac` for a given `body`), then replay that exact `body`+`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` because the signable string it checks never includes the shop domain, so the forged request is accepted and processed as if it originated from the victim tenant.

### Impact Explanation
This breaks the shop-authenticated-vs-shop-stored-as-tenant-key binding described in the rules: an unprivileged internet user who merely has a Shopify development/test store with the target app installed can forge webhook deliveries that the app believes to be tenant-authenticated for an arbitrary victim shop domain, using only a body/HMAC pair they legitimately received for their own store. Depending on how the host application's `WebhookHandler` uses `data.shop` (e.g., to look up/overwrite per-shop records, revoke access tokens, or trigger data mutations), this enables cross-tenant data confusion/writes without ever needing the victim's credentials, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only: (1) the app installed on an attacker-controlled shop (freely obtainable via a Shopify Partner/dev store), (2) capturing a single legitimate webhook body+HMAC from that shop, and (3) replaying it with a different `X-Shopify-Shop-Domain` header value to the app's public webhook endpoint. No secrets, tokens, or elevated privileges are needed, and the gem performs no additional binding between `shop` and the signed content, so the likelihood is high for any app whose webhook handler trusts `data.shop` for tenant-scoped logic.

### Recommendation
Include the shop domain (and ideally the topic and webhook id) in the HMAC-signed material, or at minimum cross-check `request.shop` against a shop that is already associated with a valid, previously-issued session/access token before invoking the handler. At a minimum, document prominently that `data.shop` is not authenticated by the webhook HMAC and must be independently verified by the host application before being used as a tenant key.

### Proof of Concept
1. App has topic `orders/create` registered; attacker installs the app on `attacker.myshopify.com`.
2. Attacker triggers an order create event on their own store; Shopify sends a POST to the app's webhook endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same body `B` and `hmac` header to the same endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` — identical to the received `hmac` — and returns `true` [5](#0-4) , so the forged request passes validation and the handler is invoked with `WebhookMetadata` carrying `shop: "victim.myshopify.com"` and the attacker's chosen `body` [6](#0-5) .

### Citations

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
