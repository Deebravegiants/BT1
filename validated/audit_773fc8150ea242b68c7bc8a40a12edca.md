### Title
Webhook `shop` identity is taken from an unauthenticated header not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` identity attached to the dispatched event is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never part of the HMAC-signed content. This breaks the equality `shop authenticated by HMAC == shop delivered to the handler`, letting any party who can produce one valid `(body, hmac)` pair for the app's shared secret relabel that payload as belonging to an arbitrary other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

`Registry.process` gates on that HMAC check alone and then constructs the dispatched `WebhookMetadata` using `request.shop`, which is simply read back from the (unsigned) `shop-domain` header: [3](#0-2) [4](#0-3) 

Because every webhook for a given app is signed with the same `api_secret_key` regardless of which installed shop triggered it, any merchant who has installed the app on their own store can legitimately trigger a webhook for themselves (e.g. `products/create`), capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair, and then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g. a victim shop). `HmacValidator.validate` still succeeds because it never inspects the shop header, and `Registry.process` hands the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-confusion vector: the library asserts to the host application's webhook handler that a given payload came from shop X, when the HMAC only proves the payload was signed with the app's shared secret — not that it originated from shop X specifically. Any host application logic that trusts `WebhookMetadata#shop` to scope multi-tenant side effects (updating shop-specific data, deactivating a shop record on `app/uninstalled`, writing order/product data keyed by shop, etc.) can be made to act on a payload while attributing it to a shop the attacker does not control, resulting in cross-tenant data corruption/impersonation.

### Likelihood Explanation
The attacker only needs to be a legitimate (if untrusted) installer of the target app on their own store — no `api_secret_key`, access token, or victim credentials are required. They only need to be able to reach the app's public webhook endpoint and reuse a body/HMAC pair they legitimately received for their own shop while swapping the shop-domain header value.

### Recommendation
Bind the `shop` value into the HMAC-verified content (or otherwise cryptographically tie it to the signed payload), for example by including the shop-domain header in `to_signable_string`, or by requiring the host application to independently confirm that the delivering shop is one it has an active installation/session for before trusting `WebhookMetadata#shop`. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook (e.g. updates a product), causing Shopify to POST a body `B` with header `x-shopify-hmac-sha256: H` (valid for the app's shared secret) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `B` — this passes.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled data is dispatched under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
