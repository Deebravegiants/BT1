## #Vulnerability Found

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by the HMAC signature, enabling shop-spoofed webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (and other metadata) used by application webhook handlers is read from an HTTP header that is excluded from the signed content. Any attacker who owns their own Shopify shop and installs the app can capture a legitimately-signed webhook (valid body + hmac for their own shop), and then replay it to the app's webhook endpoint after swapping only the `x-shopify-shop-domain` header to a victim shop domain. `Registry.process` validates only the (unchanged) HMAC and then dispatches the handler with the forged `shop`, breaking the equality "shop the HMAC authenticates" == "shop the handler acts on."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` value used downstream comes from a separate header that is never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate_signature` verifies only that the *body* matches the HMAC computed with the app's shared secret — it never binds the `shop` header: [3](#0-2) 

`Webhooks::Registry.process` performs only this HMAC check and then immediately trusts `request.shop` when building the data passed to the application's handler: [4](#0-3) 

Because the signature depends only on `(secret, raw_body)` and is completely independent of which shop the request claims to be from, any HTTP request with a body/HMAC pair that was genuinely produced by Shopify for *any* shop installed on the app will pass `HmacValidator.validate` regardless of the `x-shopify-shop-domain` (or legacy `HTTP_X_SHOPIFY_SHOP_DOMAIN`) header value included with it.

### Impact Explanation
This breaks the identity binding "shop authenticated by HMAC" == "shop acted on by the handler," which is exactly the sort of cross-tenant identity-binding gap called out in the rules. An attacker who is merely an ordinary merchant (installs the app on their own store, an action available to any unprivileged internet user with a Shopify dev/store account) can obtain a validly-signed webhook payload for events they legitimately trigger, then relay that exact payload with a forged `shop` header claiming to be a different, victim tenant. Any handler logic that uses `WebhookMetadata#shop` to select which tenant's session/data to update (a documented, intended use per `docs/usage/webhooks.md`) will act on behalf of the wrong shop — a cross-tenant integrity issue in a security-sensitive trust boundary that this gem is specifically responsible for establishing (`Registry.process` is the gem's own verification/dispatch routine, not something delegated to host-app judgment).

### Likelihood Explanation
Likelihood is meaningful: no secrets, tokens, or privileged access are required — only the ability to install the app on an attacker-owned shop (a normal unprivileged capability) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint with edited headers, both trivial for any internet user.

### Recommendation
Include the shop domain (and ideally topic and webhook id) in the value that is HMAC-verified, or otherwise independently authenticate the `shop` header/claim (e.g., verify it against a shop the app has an active, previously-established session/installation for) before trusting it in `WebhookMetadata`. At minimum, document/require that `Registry.process` callers cross-check `request.shop` against their own known-installed-shops list before acting, and consider making that check part of `Registry.process` itself.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), receiving a genuine HTTP POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (valid signature of `B`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same request to the same endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` using the app's secret and compares to `H` — this still matches because `B` and `H` are unchanged. [5](#0-4) 
4. The app's registered handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though nothing about the victim shop was ever verified — the request is processed as if it originated from the victim tenant.

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
