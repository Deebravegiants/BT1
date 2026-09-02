### Title
Webhook `shop-domain` header is trusted as tenant identity without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, but the `shop` (and `topic`/`api_version`/`webhook_id`) values consumed by `ShopifyAPI::Webhooks::Registry.process` are read from unauthenticated HTTP headers that are never part of the signed bytes. This breaks the intended binding `hmac_signed_bytes == identity_used_downstream`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`) are pulled straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC using exactly `to_signable_string`, i.e. the body bytes, and nothing else: [3](#0-2) 

`Registry.process` checks only that HMAC and then immediately trusts `request.shop` as the tenant identity passed to the app's webhook handler: [4](#0-3) 

Because Shopify webhook HMACs are computed with the app's single `api_secret_key` (the same secret for every shop/tenant that has installed the app), a party that legitimately receives a valid signed webhook for their own shop (e.g., a malicious merchant who installed the app) can replay that exact signed body while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header for a different shop domain. The signature still validates — because the signature never covered the header in the first place — yet `WebhookMetadata#shop` handed to the app's handler now claims to be the other tenant. Equality that should hold, `hmac_signed_bytes(shop) == identity(shop)`, does not: the identity field is verified independently of, and disjoint from, the signed bytes.

### Impact Explanation
This is a cross-tenant identity-confusion vector rooted entirely in this gem: it validates bytes it did not intend to bind (the body) while handing the caller-controlled, unauthenticated `shop` value on to application logic as if it were authenticated. Any host application that uses `WebhookMetadata#shop` (as documented/intended) to select per-tenant storage, sessions, or business logic can be made to process attacker-supplied body content under a different shop's identity — a cross-tenant data/logic confusion that satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitability requires only: (1) the attacker's own shop to have installed the app so they can obtain a validly-signed webhook body/HMAC pair, and (2) the ability to send an HTTP request with modified headers, which is trivial for any actor with network access to the app's webhook endpoint. No access token, `client_secret`, or privileged account is needed — only the ability to trigger any webhook topic in their own shop and resend it with a forged `shop-domain` header.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind the header-derived identity to the signed payload) so `Utils::HmacValidator.validate` cannot pass while the shop identity has been altered independently of the signed bytes.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook with body `B` and header `x-shopify-shop-domain: attacker-shop.myshopify.com`, correctly HMAC-signed over `B` with the app's `api_secret_key`.
2. Attacker captures this request and resends it to the app's webhook endpoint, keeping body `B` and the valid `x-shopify-hmac-sha256` value unchanged, but replacing the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL::HMAC.hexdigest(sha256, secret, request.to_signable_string)` against `request.hmac`; since `to_signable_string` is just `@raw_body` (unchanged), validation succeeds.
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` built from `request.shop`, causing the host application to process attacker-controlled body content attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
