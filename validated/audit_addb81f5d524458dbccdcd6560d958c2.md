### Title
Webhook `shop` and `topic` fields are not covered by the HMAC signature, allowing shop/topic spoofing on an otherwise-valid webhook - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates an incoming webhook by checking the `hmac-sha256` header against the raw request body only. The `shop-domain` and `topic` headers — which are read and trusted downstream to route the payload and identify the tenant — are never included in the HMAC-verified data. This breaks the identity binding: `bytes verified (raw body) ≠ bytes acted on (shop, topic)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `Utils::HmacValidator.validate` computes/compares the HMAC exclusively against that signable string: [2](#0-1) 

Meanwhile, `Registry.process` reads `request.shop` and `request.topic` directly from unauthenticated HTTP headers and forwards them, unbound to the signature, to the shop-specific webhook handler: [3](#0-2) [4](#0-3) 

Because the HMAC only proves the body byte-string was signed with the app's secret at some point (e.g., for the attacker's own shop's genuine webhook traffic, which a malicious app-installer can observe on their own store since they control what happens after delivery to their own infrastructure or via a temporary webhook URL they control), the `shop-domain` and `topic` headers can be swapped for an arbitrary value while keeping a still-valid `hmac-sha256` header for the same body. `Registry.process` has no independent check that the `shop` header actually corresponds to the signed payload’s origin — the equality `verified(shop) == acted_on(shop)` does not hold, since `shop` is never part of `verified`.

### Impact Explanation
An app that keys any state, authorization, or session lookup by `WebhookMetadata#shop` (the value returned by `request.shop`, as illustrated by the library's own docs and the `WebhookMetadata` construction in `Registry.process`) can be made to process a genuine-looking, HMAC-valid webhook body under an attacker-chosen tenant identity (`shop`) or an attacker-chosen `topic`, since neither is bound by the signature. This is a cross-tenant identity-confusion primitive: data legitimately signed for shop A can be relabeled as belonging to shop B (or a different topic can be claimed for the same signed payload), which can lead to cross-tenant data application in a downstream app that trusts `shop`/`topic` from `WebhookMetadata`.

### Likelihood Explanation
Exploitation requires the attacker to already possess at least one (body, valid-HMAC) pair — which any merchant who has installed the app can legitimately obtain for their own shop's webhook traffic (e.g., by controlling infrastructure between the internet edge and the app, or via replay of their own already-delivered webhook). No possession of the app's `api_secret_key` is required, since the HMAC value itself is reused unmodified; only the unsigned `shop-domain`/`topic` headers are altered. This is a moderate-likelihood, header-manipulation class of issue rather than a purely theoretical one, since it exploits a concrete gap between what is cryptographically verified and what is consumed as trusted identity.

### Recommendation
Include `shop-domain` and `topic` (and any other header fields the app relies on, such as `api-version`/`webhook-id` if they influence trust decisions) in the HMAC-signable string, or otherwise independently verify that the `shop-domain` header matches an expected/registered shop for the given HMAC before constructing `WebhookMetadata`. At minimum, document clearly that `request.shop` and `request.topic` are unauthenticated and must not be used as sole tenant/topic identifiers without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g., `orders/create`) to be delivered to the app's webhook endpoint, capturing the raw body `B` and its valid header `x-shopify-hmac-sha256: H` (computed by Shopify over `B` using the app's secret, per `lib/shopify_api/utils/hmac_validator.rb`).
2. Attacker (with a network position able to send/replay a request to the same endpoint, e.g., a controlled reverse proxy or, in a self-hosted/dev setup, by simply re-POSTing the captured request) sends a new HTTP request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid since it only covers `B`)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only checks `B` against `H`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb`, lines 188-200) builds `WebhookMetadata` with `shop: request.shop` — now `"victim-shop.myshopify.com"` — even though the payload actually originated from `attacker-shop.myshopify.com`, and dispatches it to the registered handler as if it were victim-shop's data.

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
