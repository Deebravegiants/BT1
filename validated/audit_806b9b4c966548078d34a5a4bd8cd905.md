### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read from HTTP headers that are entirely excluded from the signed content. `Registry.process` trusts `request.shop` to build the `WebhookMetadata` passed to the host app's handler, meaning the tenant-identifying value used to route/act on the webhook is never bound to the cryptographic proof that Shopify sent it.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all read from separate headers that are never mixed into that signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` (and `request.topic`) to construct the `WebhookMetadata` handed to the host app's handler — the value that determines which tenant the webhook is attributed to: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, so it is blind to the `shop-domain` header: [4](#0-3) 

This breaks the intended identity binding: `shop authenticated by HMAC == shop the handler acts on`. In reality, `shop-domain header == shop the handler acts on`, while the HMAC only proves `raw_body == raw_body signed by Shopify for the *originating* shop`. An attacker who can influence or capture what value the host application places into the `shop-domain`/`x-shopify-shop-domain` field before it reaches `ShopifyAPI::Webhooks::Request.new` (e.g., a reverse proxy, load balancer, or any component that forwards the original headers, or a legitimate webhook received by the attacker's own trial/dev shop and replayed with a different `shop-domain` header value against the same endpoint) can cause the webhook body to be attributed to a shop it was never sent for. Because `webhook_id`/`topic` used for handler dispatch are also unsigned, the attacker also has some control over how the payload is dispatched.

### Impact Explanation
This falls under "cross-tenant access": data that legitimately belongs to shop A (the raw body, which the HMAC proves came from Shopify) can be delivered to a handler under an attacker-chosen `shop`, causing the host application to process/store data or trigger side effects (order/customer/product handling, redact/GDPR flows, etc.) under the wrong tenant, or to have a "verified" webhook falsely attributed to a target shop. This is a cross-tenant identity-binding break implemented entirely within the gem's own request-parsing and dispatch logic (`Webhooks::Request` and `Webhooks::Registry.process`), not a misuse of a documented contract by the host app — the gem's own `Request` class already extracts `shop` for consumption by `WebhookMetadata` without protecting it.

### Likelihood Explanation
Exploitability depends on whether an unprivileged party can influence which header value ends up as `shopify-shop-domain` / `x-shopify-shop-domain` in the hash passed into `Request.new` for a request whose body+HMAC pair is otherwise valid (e.g., infrastructure that trusts/forwards client-supplied headers, or an attacker replaying a webhook they legitimately received for their own shop against the same endpoint but with a modified `shop-domain` header if the endpoint doesn't independently pin headers per-shop). This requires no possession of `api_secret_key`, access token, or `client_secret` — the HMAC on the replayed/forwarded body is still valid because it was never computed over the shop field to begin with.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed content that `to_signable_string` returns (or otherwise cryptographically bind them to the verified payload), or require that the host application not extract `shop` from `Webhooks::Request` for trust decisions without additional out-of-band verification (e.g., matching against the specific webhook subscription's registered endpoint). At minimum, document prominently that `Request#shop`/`#topic`/`#webhook_id` are **not** covered by HMAC verification and must not be trusted for cross-tenant authorization decisions.

### Proof of Concept
1. Attacker installs the app on their own shop, `attacker-shop.myshopify.com`, and receives a legitimate webhook whose raw body `B` is HMAC-signed by Shopify using the app's `api_secret_key`, with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: H`.
2. Attacker (or any intermediary that forwards attacker-controlled headers to the app's webhook endpoint) re-sends the exact same raw body `B` and HMAC header `H`, but overrides `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `Request.new` parses this into a `Request` object; `to_signable_string` returns `B` unchanged.
4. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `B` using the app's secret and it matches `H`, so validation succeeds: [5](#0-4) 
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with `shop == "victim-shop.myshopify.com"` and dispatches it to the handler, even though the payload was never sent by Shopify for `victim-shop.myshopify.com`: [6](#0-5) 

Note: exploitation requires a network position or infrastructure quirk that allows the attacker to control the `shop-domain` header on an otherwise-valid-HMAC request reaching this code path; this is a design/root-cause weakness in this gem's `Webhooks::Request`/`Registry` (unsigned `shop` field used for tenant dispatch) rather than a fully self-contained internet-facing exploit, since it does not by itself control what any given deployment's HTTP layer forwards as that header.

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
