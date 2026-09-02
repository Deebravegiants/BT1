### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` attribute used by `ShopifyAPI::Webhooks::Registry.process` to identify the tenant is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header. The HMAC never binds to the shop identity, so the value the app trusts for tenant attribution is not the value that was cryptographically verified.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` is validated against that signable string via `Utils::HmacValidator.validate`: [1](#0-0) [2](#0-1) 

Separately, `Request#shop` is read straight from the header dictionary with no cryptographic tie to the signed content: [3](#0-2) 

`Registry.process` validates the HMAC and, once it passes, unconditionally trusts `request.shop` to build the `WebhookMetadata` passed into the app's registered handler: [4](#0-3) 

The identity equality the gem is implicitly supposed to enforce is:
`shop authenticated by HMAC == shop used by the handler`

but in reality the code enforces only `body authenticated by HMAC == body parsed`, while `shop used by handler` is an independent, attacker-controlled input. This is structurally the same class of bug as the reported "signature replayable across domains" issue: a value that participates in application logic (shop tenant identity / chain-domain) is not included in the data that the signature actually covers, so a signature valid for one context can be replayed with a different, attacker-chosen identity value.

### Impact Explanation
An attacker who controls (or has previously received legitimate webhooks for) any single shop — including a shop they themselves install the app on — obtains a valid `(raw_body, hmac)` pair signed with the app's shared secret for that body. Because the header carrying `shop-domain` is excluded from the signed payload, the attacker can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value naming a different, victim shop. `Utils::HmacValidator.validate` still passes (it only checks the body), and `Registry.process` will invoke the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop. Any handler logic keyed off `shop` (e.g., updating per-tenant records, redacting/deleting data for `shop/redact` or `customers/redact`, provisioning resources) is executed against the wrong tenant — a cross-tenant integrity/data violation attributable purely to this gem's failure to bind the shop identity into the verified signature.

### Likelihood Explanation
Exploitation requires only knowledge of one legitimately-signed `(body, hmac)` pair for any shop (trivially obtainable by installing the app on an attacker-owned development store and capturing the webhook the app receives) and the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a forged `shop-domain` header — no access to `api_secret_key`, tokens, or the target's credentials is needed.

### Recommendation
Include the shop domain (and ideally topic/api-version) in the HMAC-covered signable content, or otherwise cryptographically bind the `shop` value to the verified body before it is handed to `WebhookMetadata`/handlers — e.g., verify the HMAC over a canonical string that concatenates the shop domain with the raw body, analogous to including a domain separator in a signature.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; the app receives a legitimate webhook `POST` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker captures `(B, H)`.
3. Attacker sends a forged request to the app's webhook endpoint with the same body `B`, the same `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (called from `Registry.process`) recomputes the HMAC over `B` only, which matches `H`, so validation succeeds.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)` and invokes the registered handler as if the payload legitimately originated from `victim.myshopify.com`. [4](#0-3)

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
