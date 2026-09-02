## Analysis

The report's bug class ("a field acted on but not covered by the HMAC") maps directly onto how this gem processes inbound webhooks.

`ShopifyAPI::Webhooks::Request` reads the `shop` (tenant) identifier straight from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header: [1](#0-0) 

But the HMAC signature that this same class exposes for verification is computed only over the raw request body, never over the shop header: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates that body-only HMAC, then immediately trusts `request.shop` as the tenant identifier and hands it to the app's handler: [3](#0-2) 

### Title
Webhook tenant (`shop`) is trusted from an unauthenticated header while the HMAC only covers the body — cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#shop` returns the value of the `x-shopify-shop-domain`/`shopify-shop-domain` header, but `HmacValidator` (invoked in `Registry.process`) only verifies the HMAC over `@raw_body` (`to_signable_string` returns `@raw_body` alone). The tenant-identifying field is not bound to the cryptographic signature at all, so it can be freely substituted by anyone who can produce (or capture) one valid `(body, hmac)` pair.

### Finding Description
The equality that should hold is: `shop authenticated by HMAC == shop the app acts on`. In this gem that equality is broken:
- LHS: HMAC validation in `HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — for `Webhooks::Request`, `to_signable_string` is just `@raw_body`. [4](#0-3) [2](#0-1) 
- RHS: `Registry.process` passes `shop: request.shop` — parsed from the `x-shopify-shop-domain` header, entirely outside the signed bytes — into `WebhookMetadata`, which is the value host applications use to attribute/act on the webhook payload (e.g. select the tenant's DB record, or run mandatory `shop/redact` / `customers/redact` compliance actions). [3](#0-2) 

Because Shopify signs webhook bodies with the same `client_secret` for a given app across every shop that installs it, any unprivileged user who installs (or has previously installed) the app on their own `myshopify.com` development shop can trigger a webhook whose body content is attacker-chosen/predictable (e.g. a webhook with a minimal or reproducible payload), capture the resulting valid `(body, hmac)` pair, then replay that exact body and HMAC to the victim app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value for a *different* shop. `HmacValidator.validate` will accept it because it only checks the body bytes, and `Registry.process` will dispatch the handler believing the event came from the spoofed shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: the library lets an attacker forge which shop a validly-signed webhook is attributed to. Depending on how the host app's `WebhookHandler` uses `WebhookMetadata#shop` (very common pattern — look up tenant record by shop, run destructive `shop/redact`/`customers/redact` flows, or write incoming order/customer data against a shop record), this enables cross-tenant data corruption, unauthorized state changes on another merchant's account, or bypass of GDPR-style redact webhook targeting — satisfying the Critical "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is non-trivial but not trivial either: the attacker needs a valid `(raw_body, hmac)` pair signed by the app's shared `client_secret`. This is achievable without any privileged credential because any user can install a public app on their own free/dev myshopify shop and receive genuinely-signed webhooks with content they influence to some degree (e.g., topics like `app/uninstalled`, `shop/update`, or ones with attacker-controlled sub-resource content), then replay the same bytes with a spoofed shop header against the victim's public webhook endpoint. No leaked secret, access token, or privileged account is required — only normal, unprivileged use of the platform.

### Recommendation
Bind the shop identity to the signature. At minimum, `Webhooks::Request#to_signable_string` (or `HmacValidator`) should incorporate a shop-domain check that is independently verifiable — e.g., cross-checking `x-shopify-shop-domain` against a shop/token known to the app (already-installed shop list) before dispatching, or requiring the host application to explicitly verify `shop` is a shop it has an active session/access token for before trusting `WebhookMetadata#shop`. The library should document (and ideally enforce) that `request.shop` must never be trusted for tenant selection without an independent installed-shop check, since Shopify's HMAC scheme for webhooks never covers headers.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, obtaining valid webhook deliveries signed with the app's real `client_secret` (same secret used for all shops).
2. Attacker triggers/observes a webhook delivery with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)` — this pair is valid because `Webhooks::Request#to_signable_string` returns `B` verbatim. [2](#0-1) 
3. Attacker POSTs body `B` with header `H` to the victim app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` instead of `attacker.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`. [5](#0-4) 
5. `Registry.process` dispatches to the registered handler with `shop: request.shop` == `"victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's shop. [6](#0-5) 
6. Any host-app logic keyed off `WebhookMetadata#shop` (tenant lookup, compliance redact flow, data writes) now operates against the wrong tenant using attacker-supplied body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
