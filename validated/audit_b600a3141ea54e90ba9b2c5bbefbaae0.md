## Analysis

The reported bug class ("value used by downstream logic differs from the value actually verified/authenticated") maps onto a genuine identity-binding gap in this gem's webhook processing.

### Root cause

`ShopifyAPI::Webhooks::Request` computes its signable content from **only the raw body**: [1](#0-0) 

The `shop` (tenant identity) is read from a separate, **unauthenticated** header and is never part of the signed content: [2](#0-1) 

`Registry.process` verifies the HMAC over the body only, then hands the **unverified** `request.shop` straight to the app's webhook handler as the tenant key, with no cross-check against anything the HMAC actually covers: [3](#0-2) 

`HmacValidator.validate` only compares the HMAC against `to_signable_string`, i.e. the raw body — it never touches `shop`: [4](#0-3) 

### Identity binding broken

The equality the gem should guarantee is:
`shop used by the handler == shop the merchant that generated/authorized this signed payload`

What is actually guaranteed is only:
`hmac == HMAC(body, secret)`

`shop` is fully decoupled from the signature. Any party capable of obtaining one legitimately-signed `(body, hmac)` pair — e.g., a merchant who installs the app themselves and receives a real webhook delivery for their own shop — can resend that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` / `shopify-shop-domain` header. `HmacValidator.validate` will still pass, because it never inspects the header, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen value while `body`/`webhook_id`/`topic` are the replayed data.

Since apps are expected (and this gem's own docs/tests show) to use `WebhookMetadata#shop` as the tenant lookup key when persisting/processing webhook data (see how `shop` is surfaced identically to `topic`/`body` in the handler contract, e.g. `data.shop` in tests), this allows a low-privilege merchant/attacker to make the app record or act on data under a **different tenant's** identity than the one Shopify's signature actually authenticated — a cross-tenant confusion, not merely a body-integrity check.

Compare this with `Auth::Oauth::AuthQuery`, where the equivalent design is done correctly: `shop` **is** included in the signed string, so the shop cannot be substituted without invalidating the HMAC: [5](#0-4) 

This asymmetry (OAuth binds `shop` into the signature, webhook processing does not) is exactly the class of bug pattern flagged: a field (`shop`) that is acted upon by the consuming code but not covered by the HMAC that is supposed to authenticate the request.

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `Utils::HmacValidator` validates the HMAC solely against that body. The `shop` (and `topic`/`webhook_id`) values are read from headers that are never included in the signed payload, yet `Webhooks::Registry.process` passes the unauthenticated `request.shop` directly to the app's webhook handler as the trusted tenant identifier.

### Finding Description
`Webhooks::Request#hmac`/`#to_signable_string` bind the signature exclusively to `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`). `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) only recomputes and compares against that signable string. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) checks this HMAC and then constructs `WebhookMetadata.new(shop: request.shop, ...)` using the header-derived, unauthenticated `shop` value. Any entity that legitimately receives one signed webhook (e.g., by installing the app on their own store) can resubmit that identical `(body, hmac)` pair to the app's webhook endpoint with a forged `shop` header, and the gem will report the webhook as valid and hand the handler a `shop` value that was never actually verified by the signature.

### Impact Explanation
This breaks the identity binding between "the shop Shopify actually signed this payload for" and "the shop the app is told to act on," enabling cross-tenant data processing/confusion inside apps that trust `WebhookMetadata#shop` as their tenant key (the intended and documented usage of this field).

### Likelihood Explanation
Requires the attacker to possess at least one genuinely-signed webhook body/HMAC pair (achievable simply by installing the app as an ordinary merchant and receiving any webhook), then replaying it directly to the app's public webhook endpoint with a modified shop header — no access to `api_secret_key` or any privileged credential is required.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or independently cross-check `request.shop` against a known/registered session store before dispatching to the handler, so that a mismatched or replayed shop header cannot be forwarded as trusted tenant identity.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggers any webhook event, and captures the delivered `raw_body` and `X-Shopify-Hmac-Sha256` header — both are valid together.
2. Attacker POSTs this exact `raw_body` + `hmac` to the app's webhook endpoint again, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` → `HmacValidator.validate` succeeds (only `raw_body` is checked), and the handler receives `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the payload was never signed for that shop.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
