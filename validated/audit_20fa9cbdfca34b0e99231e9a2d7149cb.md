### Title
Webhook `shop` (and `topic`/`webhook-id`) fields are trusted for tenant routing but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` proves nothing about the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, or `x-shopify-api-version` headers. `Registry.process` nonetheless treats `request.shop` as an authenticated tenant identifier and hands it straight to the handler via `WebhookMetadata`.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) [2](#0-1) 

`to_signable_string` returns `@raw_body` only - it never includes `shop`, `topic`, `webhook_id`, or `api_version`. `HmacValidator.validate_signature` computes/compares the HMAC strictly against that signable string: [3](#0-2) 

`Registry.process` uses the HMAC check purely as a gate, then immediately trusts `request.shop` (read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header) to build the tenant-identifying `WebhookMetadata` object passed to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop used to authorize/act on webhook data == shop cryptographically bound to the payload via HMAC`

In this implementation that equality never holds: HMAC binds `{body}` to `{secret}`, but the `shop` value acted upon by the handler comes from a header that is completely outside the HMAC's scope. A merchant who has legitimately installed the app on their own store `shop-A` can capture a genuine, correctly-signed webhook (body + valid `x-shopify-hmac-sha256`), then replay that exact body/HMAC pair to the app's public webhook endpoint while substituting `x-shopify-shop-domain: shop-B.myshopify.com` (a different, victim tenant that also uses the same app). `HmacValidator.validate` still returns `true` because it only checked the untouched body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "shop-B.myshopify.com"` with attacker-chosen body content (the attacker fully controls their own store's webhook payload content, e.g., product/order fields).

### Impact Explanation
This breaks the cross-tenant isolation the HMAC check is meant to guarantee: an unprivileged actor who is merely a legitimate customer/merchant of their own tenant can forge webhook events that the app will process as belonging to a different, arbitrary tenant, because the gem only validates the body and gives the caller a false sense that the whole request (including `shop`) has been authenticated. Any downstream logic that keys writes, lookups, notifications, or access-token usage off `WebhookMetadata#shop` is exposed to cross-tenant data confusion/corruption, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Requires only: (1) the attacker to install/operate their own shop with the target app, so they can obtain one authentic HMAC-signed webhook payload of their choosing, and (2) the ability to send an arbitrary HTTP request to the app's public webhook receiving endpoint with a modified `shop-domain` header — no access token, `api_secret_key`, or victim credentials are needed. This is straightforward for any internet-reachable webhook endpoint.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified signable content, or require the caller to independently confirm that `request.shop` matches an already-authenticated session/shop record before trusting it, rather than deriving tenant identity solely from an unauthenticated header alongside a body-only HMAC check.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`; app registers a webhook (e.g. `products/update`).
2. Attacker edits a product they own so Shopify sends a webhook with body `B` and a valid `x-shopify-hmac-sha256` computed by Shopify using the real `api_secret_key`.
3. Attacker captures this raw request (`body: B`, `hmac: H`).
4. Attacker replays the request to the app's webhook endpoint, keeping `body: B` and `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-hashes `B` and compares to `H` — validation succeeds: [5](#0-4) 
6. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, causing the app to act on forged data under the victim's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
