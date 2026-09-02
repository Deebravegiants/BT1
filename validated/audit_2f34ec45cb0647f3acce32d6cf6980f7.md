### Title
Webhook shop/topic identity spoofing via HMAC that only signs the body, not headers - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC only covers the raw body. The `shop`, `topic`, `webhook_id`, and `api_version` values used to dispatch the webhook to a handler are taken from unauthenticated HTTP headers that are never bound to the HMAC.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

While `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, independent of the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature only over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` accepts the request as legitimate once the body-only HMAC check passes, then dispatches using the unauthenticated `shop` header: [4](#0-3) 

Because the HMAC secret (the app's `client_secret`) is shared across every shop that has the app installed, any merchant that installs the app on their own store receives genuine webhooks with a valid `(body, hmac)` pair for that body. That merchant can replay the exact same `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. The HMAC check still passes because it never covers the `shop` header, so `Registry.process` builds `WebhookMetadata` attributing attacker-controlled body content to the victim tenant: [5](#0-4) 

The binding that is broken is: `shop-attribution-used-by-handler == shop-bytes-covered-by-HMAC`. The left side is the header value trusted by every downstream handler; the right side is empty, since only the body is signed.

The gem's own documentation compounds this by claiming the opposite: `Registry.process` "will verify the request did indeed come from Shopify," implying the full request (including the shop attribution) is verified, when only the body bytes are: [6](#0-5) 

### Impact Explanation
This is a cross-tenant identity-confusion vector: data legitimately signed for shop A can be injected into shop B's webhook processing pipeline simply by changing an unauthenticated header, without needing the app's `client_secret`. Any app that persists webhook payloads keyed by `data.shop` (the documented, intended usage per `docs/usage/webhooks.md`) can have another tenant's data associated with the wrong shop, corrupting per-tenant state or triggering shop-scoped side effects (e.g., background jobs, DB writes) for a shop that never actually sent that payload.

### Likelihood Explanation
Likelihood is meaningful: exploitation requires only that the attacker be a legitimate, unprivileged merchant who has installed the target app (a standard, freely available action for any Shopify app), and standard HTTP tooling to replay a captured `(raw_body, hmac-sha256 header)` pair with a modified `shop-domain` header. No access to the app's `client_secret`, TLS interception, or social engineering is needed.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) to the HMAC verification, e.g. by including these header values in the signable string used for signature verification, or by cross-checking that the webhook's `shop` matches a shop for which this exact topic/webhook_id combination was registered before invoking the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — this HMAC is valid because it is computed with the app's shared `client_secret` over the body only.
2. Attacker replays the exact same body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the signature over the body only and it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) proceeds and invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker-supplied body content, even though `victim-shop` never sent this webhook.

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
