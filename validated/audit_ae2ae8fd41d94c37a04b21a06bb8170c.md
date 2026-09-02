This confirms the doc explicitly claims `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify," which sets the security expectation that the entire `Request` (including `shop`, `topic`, `webhook_id` headers) is authenticated. Let me confirm the exact boundary and check `VerifiableQuery`.This confirms the root cause clearly enough. I have what I need to write the final answer.### Title
Webhook shop/topic/webhook-id identity is not covered by the HMAC, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," but the HMAC signature computed by `Utils::HmacValidator` only authenticates the raw request body — it never binds the `shop-domain`, `topic`, or `webhook-id` headers that `Registry.process` and the app's handler treat as authoritative identity data.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop`, `topic`, `webhook_id`, `api_version` are all pulled straight from unauthenticated HTTP headers with no cryptographic tie to the body or to each other: [2](#0-1) 

`Registry.process` validates only this body-derived HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` confirms this — it signs/verifies only `verifiable_query.to_signable_string`, i.e., the body for webhooks: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:

`HMAC_secret(raw_body)` is treated by the caller as authenticating `(shop, topic, webhook_id, raw_body)`, but it actually only authenticates `raw_body`. Concretely: `valid_hmac(body, shop=A) == valid_hmac(body, shop=B)` for any `shop-domain` header value, because `shop` never enters the signable string.

This means the app's `client_secret` (a single shared HMAC key across every shop of the app) produces the same valid signature for a webhook body regardless of which shop's domain is claimed in the header. The gem's own documentation, `docs/usage/webhooks.md`, tells integrators that `Registry.process` "will verify the request did indeed come from Shopify," which is the security guarantee that this identity binding violation breaks — this is not the host application ignoring the documented API, it is the gem's documented guarantee not matching its implementation.

### Impact Explanation
An unprivileged internet user who is a legitimate merchant using the app on their own store receives real webhook deliveries from Shopify with a body and a valid HMAC signed by the app's single shared `client_secret`. Because the HMAC covers only the body, that attacker can capture one of their own legitimate webhook deliveries (body + HMAC), then POST the identical body and HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header to name a victim shop. `HmacValidator.validate` still succeeds because it never inspects the headers, and `Registry.process` hands the forged `shop` value straight to the app's handler as authenticated data. Any host application that keys its persistence, authorization, or business logic on `WebhookMetadata#shop` (exactly as the gem's own documented example does: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process attacker-supplied data under another tenant's identity — a cross-tenant data-injection/access primitive, achievable with no access token, no `client_secret`, and no privileged account, only participation as a normal installed merchant of the app.

### Likelihood Explanation
High practical likelihood: the webhook HTTP endpoint is by design internet-reachable and unauthenticated apart from the HMAC check; obtaining one's own valid webhook payload/HMAC pair requires nothing more than installing the app on a store the attacker controls (or observing any webhook the app already receives, since the same `client_secret` signs every shop's webhooks); and no rate limiting/anti-replay/timestamp binding exists in `Request`/`HmacValidator` to prevent header substitution or replay across shops.

### Recommendation
Bind the identity headers into the signable material (or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the HMAC-covered payload) before trusting them in `Registry.process`/`WebhookMetadata`, e.g., include the canonicalized headers in `to_signable_string`, or require the host application to independently verify `shop` against a known/authorized shop list (session store) before acting on webhook data. At minimum, update `docs/usage/webhooks.md` to stop asserting that `Registry.process` verifies the full request when in fact only the body is authenticated, and add a nonce/timestamp + header-binding scheme to prevent cross-shop replay.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and legitimately receives a webhook, e.g. body `{"id":1}` with header `x-shopify-hmac-sha256: <H>` where `H = HMAC-SHA256(client_secret, '{"id":1}')`.
2. Attacker sends a forged POST to the app's public webhook endpoint reusing the same raw body `{"id":1}` and the same `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and any desired `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers into `shop = "victim-shop.myshopify.com"`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, '{"id":1}')` and compares it to `H` — this succeeds because the shop header is not part of the signed string: [5](#0-4) 
5. The registered handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: {"id"=>1}, ...)`, and the host application (following the gem's own documented pattern of keying work off `data.shop`) processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
