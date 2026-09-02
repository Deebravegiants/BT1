### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then hands the caller-supplied `shop` header straight to the app's handler without any cryptographic binding to that same HMAC. Any party who can produce one valid `(raw_body, hmac)` pair for the app's secret (e.g. by installing the app on their own store and receiving one legitimate webhook) can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header, and the gem will accept it as an authenticated webhook "from" that arbitrary shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read directly from an unauthenticated header: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` compute the signature over `verifiable_query.to_signable_string`, i.e. the body only — none of the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) are part of the signed material: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authentication for the whole request, then forwards the unauthenticated `request.shop` value into `WebhookMetadata`, which is exactly what host apps use to determine which tenant/session the webhook belongs to: [4](#0-3) 

This breaks the expected identity binding `hmac_verified(body) == authenticated(shop)`. In reality the gem only proves `hmac_verified(body)`; `shop` is taken on faith from a plain header that travels alongside the signed body but is never covered by the signature.

### Impact Explanation
An unprivileged internet user who is able to install the target app on any shop they control (a normal, unprivileged onboarding action, not requiring any of the app's secrets) will receive at least one legitimate webhook delivery containing a valid `(raw_body, hmac)` pair signed with the app's `client_secret`. Because the signature never covers the `shop-domain` header, that same body+HMAC pair remains valid no matter what shop domain is placed in the header. The attacker can replay the captured request to the app's webhook endpoint with the header rewritten to any victim shop's domain. `Registry.process` will pass the HMAC check and dispatch the handler with `WebhookMetadata#shop` equal to the attacker-chosen victim shop. Any host application that uses `data.shop` from `WebhookMetadata` to look up the victim's session/access token and perform actions (e.g. update local data keyed by shop, trigger side effects scoped to that shop) will act under an attacker-controlled tenant identity — a cross-tenant confusion primitive. This meets the High-impact bar ("cross-tenant access" / identity-binding bypass) defined for this assessment.

### Likelihood Explanation
Exploitation requires only steps available to any unprivileged internet user: installing the app on a store they control to receive one legitimate webhook, then replaying/crafting an HTTP POST with a modified shop-domain header. No possession of `api_secret_key`, access tokens, or any privileged credential of the victim is needed — only knowledge of one's own legitimately-received `(body, hmac)` pair, which is by design visible to the shop owner who installed the app.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signed material, or otherwise cryptographically bind the `shop` value to the verified body before it is handed to handlers — e.g., require the host app to additionally verify that the shop presented in the webhook matches a shop with an active/expected session before trusting `WebhookMetadata#shop`, or have `HmacValidator`/`Request` incorporate the shop-domain header into `to_signable_string` so a mismatched header invalidates the HMAC.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-service, unprivileged).
2. Shopify sends a legitimate webhook to the app: body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker replays the exact same request to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new` parses headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` — still equal to `H` because the header is not part of `to_signable_string` — so validation passes: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the request never originated from Shopify on behalf of that shop.

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
