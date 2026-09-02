Confirmed: `handler.handle` is called with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` at [1](#0-0)  where `request.topic`, `request.shop`, `request.webhook_id`, and `request.api_version` are all read directly from HTTP headers via `shopify_header` at [2](#0-1)  while the HMAC is computed only over the raw body via `to_signable_string` at [3](#0-2) .

### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by re-computing an HMAC over the raw request body and comparing it to the `X-Shopify-Hmac-Sha256` header. The `shop`, `topic`, `webhook_id`, and `api_version` values that the gem hands to the host application's handler (via `WebhookMetadata`) come from separate, unsigned HTTP headers. Because the HMAC never binds these header values to the body, they can be swapped freely without invalidating the signature.

### Finding Description
`Utils::HmacValidator.validate` at [4](#0-3)  calls `verifiable_query.to_signable_string` and compares against `verifiable_query.hmac`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [3](#0-2) , while `hmac` is parsed from the `hmac-sha256` header [5](#0-4) . The `shop`, `topic`, and `webhook_id` accessors read directly from other, independent headers [2](#0-1) , none of which are included in the signed bytes.

`Registry.process` uses `Utils::HmacValidator.validate(request)` to gate processing, then immediately trusts `request.topic` to select a handler and `request.shop` to construct the `WebhookMetadata` passed to that handler [1](#0-0) .

Crucially, the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that installs the app — it is not per-shop. This means the "bytes verified" (only the JSON body) are decoupled from the "bytes acted on" (the shop-domain header used to attribute the webhook to a tenant). The binding that should hold is: `shop header used for tenant dispatch == shop cryptographically bound by the HMAC`. Instead it only holds: `HMAC(body, shared_secret) == signature`, with `shop`/`topic`/`webhook_id` unauthenticated.

### Impact Explanation
Any shop that installs the app (an ordinary, unprivileged tenant, exactly analogous to any user who can obtain a merchant account) can capture one genuine webhook delivered to its own endpoint. That delivery carries a body and a valid HMAC computed with the app's single shared `client_secret`. The attacker can then replay that exact body/HMAC pair to the app's webhook endpoint while rewriting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) headers to any other tenant's shop domain. `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` will dispatch to the handler with `WebhookMetadata#shop` set to the victim's domain and body content controlled by the attacker (within the constraints of a topic they can produce, e.g. replaying an `orders/create` payload but claiming it is for shop B). Host applications built on this gem's documented `Registry`/`Request` API reasonably treat `WebhookMetadata#shop` as authenticated once HMAC validation passes — this gem provides no indication that the shop attribution is unauthenticated. This is a cross-tenant integrity violation: an attacker can inject/attribute falsified webhook events to a shop they do not own, corrupting tenant-scoped state (e.g., synthetic `orders/create`, `app/uninstalled`, `shop/redact`) using only capabilities any installing merchant already has.

### Likelihood Explanation
Any actor able to install the target app on a shop (a normal, unprivileged onboarding flow, not requiring leaked credentials or admin access) can obtain at least one legitimately HMAC-signed webhook body/signature pair and then freely re-attribute it to an arbitrary shop domain by editing unauthenticated headers when replaying the request to the app's own webhook endpoint.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook-id` header values inside the HMAC-covered `to_signable_string` (or otherwise cryptographically bind them, e.g. via a canonicalized string combining headers + body) so that any header used for tenant/topic attribution cannot be altered without invalidating the signature. Alternatively, verify these header values only against Shopify-known/shop-registered app-install records rather than trusting the header value blindly once the raw-body HMAC passes.

### Proof of Concept
1. Attacker installs the target Shopify app onto their own store `attacker-shop.myshopify.com`.
2. Attacker triggers (or waits for) a genuine webhook delivery, e.g. `orders/create`, and captures the raw request: body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker resends the exact same request to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and optionally alters `X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and finds it matches `H` — validation succeeds [6](#0-5) .
5. The registered handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, even though this data never originated from, nor was cryptographically bound to, `victim-shop.myshopify.com` [7](#0-6) .

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
