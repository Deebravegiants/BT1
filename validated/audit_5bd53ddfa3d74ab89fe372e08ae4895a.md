### Title
Webhook tenant identity (`shop-domain`) is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to attribute the payload to a tenant. Because the signed material excludes the shop identifier, any actor who can produce one valid `(body, hmac)` pair can replay it with an arbitrary `shop-domain` header and have the library accept it as belonging to a different shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is read directly from an unauthenticated header: [2](#0-1) 

`HmacValidator.validate_signature` computes and compares the signature exclusively against `verifiable_query.to_signable_string` (the body), never incorporating `shop`: [3](#0-2) 

`Registry.process` accepts the request once the body HMAC checks out, then forwards the attacker-controllable `request.shop` straight to the app's webhook handler as the tenant identifier: [4](#0-3) 

This exactly matches the reported bug class: a field the application acts on (`shop`, used to attribute/route the webhook payload to a specific merchant) is not covered by the same authentication mechanism (`hmac`) that is used to prove the request's authenticity. The equality that should hold — `shop bound by HMAC == shop used to process data` — is broken: the HMAC only proves "this body was signed with the api_secret_key by *some* legitimate source (any shop with the app installed)", not "this body belongs to shop X".

### Impact Explanation
Any unprivileged internet user who can install the target app on their own (attacker-controlled) shop can trigger a real webhook delivery and obtain a valid `(raw_body, hmac)` pair signed with the shared `client_secret`. They can then send that same body/HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop, since `shop` is taken from `request.shop` (line 198) independent of the signature check. If the consuming application uses this `shop` value to key data (create/update/delete records, trigger side effects, etc. — the documented and intended use of `WebhookMetadata#shop`), this allows cross-tenant data injection/corruption without ever compromising the victim or obtaining their credentials.

### Likelihood Explanation
Exploitation requires only an app installation on an attacker's own store (obtainable by any developer/merchant on the Shopify platform for public or even development apps) plus the ability to POST directly to the app's public webhook URL — no privileged access, token theft, or TLS interception is needed. The gem itself provides no cross-check between the authenticated body and the header-derived `shop`, so every consumer of `ShopifyAPI::Webhooks::Registry` inherits this gap.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header in the signed material verified by `HmacValidator`, or otherwise cryptographically bind the tenant identity to the payload before dispatching to `handler.handle`, so that a valid signature can only be replayed for the shop it was actually issued for.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook (e.g., `products/create`) to receive a legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair signed with the app's `client_secret`.
2. Construct a new HTTP POST to the app's webhook endpoint reusing the same `raw_body` and `X-Shopify-Hmac-Sha256` value, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers/body, `Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the secret (`lib/shopify_api/webhooks/registry.rb:190`), and `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"`, `body: request.parsed_body` — data the attacker fully controls, now attributed to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
