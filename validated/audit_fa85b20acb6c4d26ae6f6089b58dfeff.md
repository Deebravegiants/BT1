### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are trusted for tenant routing while excluded from the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload solely from the raw request body, while the `shop-domain`, `topic`, and `webhook-id` values are read from unauthenticated HTTP headers. `Registry.process` trusts these header values to route the webhook to app handlers and to build the `WebhookMetadata` that identifies which tenant (shop) the payload belongs to, without any check that the header-asserted shop is the one that actually produced the signed body.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates only that the body's HMAC is correct, then immediately uses the unauthenticated `request.shop` and `request.topic` to dispatch to the tenant-specific handler: [3](#0-2) 

Because `Context.api_secret_key` is a single, app-wide secret shared across every shop that has installed the app (it is not per-shop), any merchant who has legitimately installed the app can obtain a validly-HMAC'd `(body, hmac)` pair for their own store's webhook traffic. Since the `shop-domain` header sits entirely outside the signed material, that same valid `(body, hmac)` pair can be replayed against the app's webhook endpoint with the `shop-domain` header rewritten to point at a different victim shop. `HmacValidator.validate` will still pass because it only recomputes the HMAC over `@raw_body`: [4](#0-3) 

The equality that should hold is:
`shop asserted to the handler (request.shop, from header) == shop whose secret/context actually authenticated the signed bytes`

That equality is never checked — the HMAC only proves "this body was signed with the app's secret sometime, by someone," not "this body belongs to shop X."

### Impact Explanation
This breaks the shop/tenant identity binding used by every consumer of `WebhookMetadata`. An app author building webhook handlers around `data.shop` (as the docs and the gem's own API push them to, e.g. `data.shop` used to look up per-shop sessions/records) can be induced to process a genuine, cryptographically-valid webhook body under the wrong shop's identity, leading to cross-tenant data confusion (e.g., writing/attributing customer or order data to a different merchant's tenant, or triggering the `customers/redact`/`shop/redact` mandatory compliance handlers for the wrong store). This falls under cross-tenant access under the stated High/Critical impact bar.

### Likelihood Explanation
Exploitation requires only that the attacker be a genuine (unprivileged, non-admin) merchant with the target app installed in their own store — no access token, API secret, or privileged account for the *victim* shop is needed. They can capture one of their own store's legitimate webhook deliveries (valid body + valid HMAC) and resend it to the app's public webhook endpoint with a modified `X-Shopify-Shop-Domain` header. This is a low-effort, purely network-level replay once the attacker controls any one shop using the app.

### Recommendation
Bind the shop (and topic) into the signed material, or otherwise authenticate the header out-of-band: e.g., look up the expected shop from the app's own session/installation store using the webhook body's `id`/context rather than trusting the header, or require the app to independently verify that `request.shop` corresponds to an installation whose access token was used to register that specific webhook subscription. At minimum, document prominently that `request.shop` is unauthenticated and must not be used as a tenant boundary without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app in `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g., updates a product) and captures the raw POST body plus the `X-Shopify-Hmac-Sha256` header sent by Shopify to the app's webhook endpoint.
3. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `@raw_body` against the HMAC.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the app's handler, which now processes attacker-controlled data under the victim's tenant identity.

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
