### Title
Webhook `shop-domain` (tenant identity) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC that `HmacValidator.validate` checks authenticates *only the body bytes*, never the `shop-domain` header that the registry trusts as the webhook's tenant identity.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the received HMAC using `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be exactly `@raw_body`: [2](#0-1) 

The `shop` (tenant identity), `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers and are **not** included in `to_signable_string`, and therefore are not covered by the HMAC at all: [3](#0-2) 

`Registry.process` validates only this body-only HMAC, then hands the unauthenticated `request.shop` header straight to the app's webhook handler as the authoritative tenant identity: [4](#0-3) 

The identity binding this breaks is: `hmac_verified(bytes) == shop_trusted_for_tenant_routing`. The gem verifies the *body* bytes but trusts the *shop-domain header* as the tenant identifier for dispatching to per-shop handler logic, and these two things are never cryptographically bound together.

### Impact Explanation
An attacker who operates their own (legitimately installed) shop can generate a real webhook — with a real, validly-computed HMAC for an arbitrary body/topic (e.g. `customers/redact`, `shop/redact`, `orders/create`) signed with the app's real `client_secret` (Shopify computes and sends this HMAC to any installed shop). The attacker intercepts/replays this HTTP request to the app's webhook endpoint, changing only the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header to a victim shop's domain. Because that header is excluded from the signable string, `HmacValidator.validate` still returns `true`, and `Registry.process` will invoke the handler with `WebhookMetadata.new(topic: ..., shop: <victim-shop>, body: ..., ...)`, causing the host application to process attacker-controlled data under another tenant's identity — a cross-tenant confusion at the point where this gem hands off "authenticated" webhook data to the app.

This lets an attacker impersonate any shop to the app's own webhook processing logic despite HMAC verification succeeding, which matches the Critical cross-tenant access category.

### Likelihood Explanation
Any developer/merchant can install the target app on a shop they control and thus obtain real webhook deliveries (body + valid HMAC) signed with the shared `client_secret`. Modifying an unsigned header on replay requires no secret material and no privileged access — only the ability to send an HTTP request to the app's public webhook endpoint, which is by design internet-reachable.

### Recommendation
Bind the tenant identity into the signed payload verification: derive `shop` used for dispatch from a value that is cryptographically tied to the signature (e.g., include the `shop-domain`, `topic`, and `webhook-id` headers in the signable string used for HMAC computation, matching what Shopify actually signs), or verify the `shop` value against session/registration state established independently of headers before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and configures a webhook subscription (e.g. `orders/create`).
2. Shopify delivers a webhook to the app with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and some JSON body.
3. Attacker intercepts this request before it reaches the app (or crafts a matching request), and replays it to the app's webhook endpoint after rewriting only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, leaving body and HMAC header untouched.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `@raw_body`, unchanged) and succeeds: [4](#0-3) 
5. The handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"`, even though the payload was never actually sent by Shopify on behalf of that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
