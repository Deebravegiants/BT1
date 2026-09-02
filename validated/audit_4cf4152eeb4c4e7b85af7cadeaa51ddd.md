### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then trusts the `shop-domain` header (and `topic`, `webhook-id`, `api-version` headers) to determine which merchant/tenant the payload belongs to. None of those headers are included in the HMAC-signed data, so a request whose body+HMAC pair is legitimate for one shop can be replayed with a different `shop-domain` header and will still pass validation while being attributed to an arbitrary tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string (the body) and compares it against the `hmac-sha256` header value: [2](#0-1) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read directly from unauthenticated HTTP headers, independent of the signed bytes: [3](#0-2) 

`Registry.process` performs the HMAC check and then immediately trusts `request.shop` (and `request.topic`) as the tenant identity when dispatching to the registered handler, passing them into `WebhookMetadata` alongside the parsed body: [4](#0-3) 

This breaks the intended identity binding: `hmac(raw_body) == HMAC-SHA256(client_secret, raw_body)` says nothing about `shop-domain == <the tenant this body belongs to>`. Any request whose `raw_body` + `hmac-sha256` header form a valid pair — which is trivially available to anyone who has legitimately received (or captured) one real webhook delivery from Shopify for any shop that has the app installed, including the attacker's own store — can be re-sent to the app's webhook endpoint with the `shop-domain` header (and `topic`/`webhook-id` headers) swapped to name a different shop. `Registry.process` will validate the HMAC successfully (since it's still checking the untouched, valid body) and then hand the handler a `WebhookMetadata` claiming to be from the victim shop.

This mirrors the reported bug class: a caller (`Registry.process`) acts on a field (`shop-domain`/`topic` headers) that is not covered by the integrity check (the HMAC only spans the body), so the identity actually authenticated (a valid body signed for shop A) diverges from the identity the code trusts and acts on (shop B, taken from an unauthenticated header).

### Impact Explanation
If a host application relies on `WebhookMetadata#shop` (as returned by this gem's own `Registry.process`/`Request` API) to select which merchant's data/session to update inside its webhook handler — which is the documented and expected usage pattern — an attacker can forge the tenant attribution of a webhook delivery without possessing the app's `client_secret`. This is a cross-tenant confusion: data intended for/about shop A can be injected and processed as if it belongs to shop B, e.g., triggering handlers that write cache invalidation, mandatory-topic bookkeeping, or app state keyed by `shop`, corrupting or leaking cross-tenant application state. This falls under the Critical "cross-tenant access" impact category defined in scope.

### Likelihood Explanation
Likelihood is constrained by the fact that the attacker needs at least one legitimately signed `(raw_body, hmac-sha256)` pair to replay — but this is easy to obtain: any store owner who installs the target app (a completely unprivileged action available to any internet user for public/free apps) will receive real, validly-signed webhooks from Shopify for their own store. They can then replay that exact body/HMAC pair against the app's public webhook endpoint while substituting a different `shop-domain` (and topic) header value. No secret material, TLS interception, or privileged account is required — only normal, self-service app installation plus header manipulation on an HTTP request they fully control.

### Recommendation
Bind the tenant-identifying headers into the HMAC-verified data rather than trusting them independently. Options:
- Include `shop-domain`, `topic`, and `webhook-id` in `Request#to_signable_string` (i.e., sign header+body concatenation) so any tampering invalidates the HMAC, or
- Have `Registry.process`/`WebhookMetadata` cross-check `request.shop` against an independently trusted source (e.g., look up the session/shop the handler is registered for, or validate that the shop is one that is expected to be sending webhooks for that specific delivery) instead of trusting the header verbatim, or
- At minimum, document prominently that `request.shop`/`request.topic` are NOT covered by the HMAC and must not be used as the sole tenant selector without additional verification (e.g., matching against a known/allow-listed shop for that webhook subscription id).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (a normal, unprivileged action) and enables a webhook topic (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`
   - Body: `raw_body` (JSON order payload)
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value (they own this request; no interception needed).
4. Attacker re-sends a new HTTP request to the same app endpoint with the identical `raw_body` and `x-shopify-hmac-sha256` header, but changes `x-shopify-shop-domain` to `victim.myshopify.com` (a real shop that also has the app installed).
5. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request object; `Utils::HmacValidator.validate(request)` recomputes the HMAC over `raw_body` only, which still matches, so validation passes: [5](#0-4) 
6. `Registry.process` dispatches the handler with `shop: request.shop` equal to `"victim.myshopify.com"` and `body: request.parsed_body` (the attacker's own order payload), even though Shopify never sent this data for `victim.myshopify.com`. The application-level handler now processes attacker-controlled data under the victim's tenant identity. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
