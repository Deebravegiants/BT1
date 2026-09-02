### Title
Webhook `shop`/`topic`/`webhook-id` headers are not covered by the HMAC signature, allowing cross-tenant webhook impersonation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content solely from the raw HTTP body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to route and process the webhook are read from unauthenticated HTTP headers that are never part of the HMAC-verified bytes.

### Finding Description
`Webhooks::Registry.process` authenticates an inbound webhook by calling `Utils::HmacValidator.validate(request)` [1](#0-0) , which computes an HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` header via a constant-time comparison [2](#0-1) .

Critically, `Request#to_signable_string` returns **only the raw body**: [3](#0-2) 

Yet `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled straight from request headers that are completely outside that signed string: [4](#0-3) 

After the HMAC check passes, `Registry.process` immediately trusts `request.shop` and `request.topic` to dispatch to the registered handler and to build `WebhookMetadata`, which is handed to the host application's business logic keyed by shop: [5](#0-4) 

The equality the code implicitly assumes is:
`bytes verified by HMAC (raw_body) == bytes the app trusts as the tenant/topic identity (shop-domain header, topic header)`

This equality does not hold: the `shop-domain`/`topic`/`webhook-id` headers can be freely modified without invalidating the HMAC, because they were never part of the signed material in the first place.

### Impact Explanation
Because the app-level `api_secret_key` is shared across all shops that install the app (it is not a per-shop secret), any party who has legitimately obtained one valid `(raw_body, hmac)` pair — for example, by installing the app on their own store and observing a genuine webhook delivery — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` and/or `x-shopify-topic` header. `HmacValidator.validate` will still return `true` because it only checks the body against the HMAC, so `Registry.process` will invoke the handler with attacker-chosen `shop`/`topic` values in `WebhookMetadata`. Any host application logic that partitions data per-tenant based on `WebhookMetadata#shop` (the documented and expected use of this field) can be tricked into attributing attacker-controlled webhook content to a different merchant's tenant, i.e. cross-tenant data confusion/injection.

### Likelihood Explanation
Exploitation requires only: (1) obtaining one legitimate `(body, hmac)` pair from any shop that has the app installed (trivially available to any developer who installs the app, including on a free/dev store), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers — both are actions available to an unprivileged internet user with no access to `api_secret_key`, tokens, or the target's credentials.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string that is HMAC-verified (or otherwise independently bind them, e.g., by verifying the `shop` header against the session/tenant expected to own the given webhook subscription) so that tampering with these headers invalidates the signature.

### Proof of Concept
1. Install the target app on shop `attacker-shop.myshopify.com` and capture one real webhook delivery, e.g. `orders/create`, noting the raw body `B` and the `x-shopify-hmac-sha256` header `H` (valid because `H = HMAC(api_secret_key, B)`).
2. Send a new POST request to the app's webhook endpoint with the *same* body `B` and *same* header `H`, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and/or change `x-shopify-topic` to a different registered topic).
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` (`lib/shopify_api/webhooks/request.rb` `to_signable_string`), so `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
