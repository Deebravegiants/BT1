## Title
Webhook `shop` identity is read from an unauthenticated header while the HMAC only covers the raw body - (`lib/shopify_api/webhooks/request.rb`)

### Summary
The bug-class in the referenced report is a broken identity binding: an actor-controlled field (`_collections.isForSale`) is not covered by the check that is supposed to authenticate the caller, so a front-runner can smuggle in their own value while riding on someone else's transaction. The analogous binding in this gem is between the webhook's cryptographic signature and the `shop` identity that the SDK hands to the application's webhook handler. `ShopifyAPI::Webhooks::Registry.process` treats a request as authentic once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC is computed only over the raw body, never over the `shop` (or `topic`) that the handler receives.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header with no cryptographic tie to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only re-computes the HMAC over `verifiable_query.to_signable_string` (i.e. the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` gates entirely on that body-only HMAC check, then forwards the untrusted `request.shop` header value straight into the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because `shop` (and `topic`) are excluded from the signed bytes, the equality the SDK implicitly promises to callers — "HMAC valid" ⇒ "`shop` is the tenant Shopify actually sent this for" — does not hold. Anyone who can obtain one genuine `(body, hmac)` pair for their *own* shop (trivial: install the app on a free dev store and trigger a webhook) can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value, since that header is never part of what's authenticated.

### Impact Explanation
This breaks the tenant/shop identity boundary: an attacker can make the SDK report to the host application's webhook handler that a forged payload originated from a victim shop, when in fact only the attacker's own genuine webhook signature was reused. Any host application logic keyed off `WebhookMetadata#shop` (e.g. looking up the victim's session/access token to act on their behalf, or writing data attributed to the victim shop) can be poisoned this way. This is a cross-tenant data/identity confusion class in the same family as the reported "identity can be swapped underneath a validated action" bug.

### Likelihood Explanation
Requires only unprivileged internet access plus the ability to install the target app on any shop the attacker controls (or otherwise obtain one valid webhook), and the ability to send arbitrary HTTP requests to the app's public webhook endpoint (which is inherently internet-reachable). No access token, `client_secret`, or privileged credentials are required — only the app's already-known ability to receive webhooks.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the signed/verified material, or otherwise cryptographically or out-of-band bind the shop identity to the specific HMAC before it is exposed to consumers via `WebhookMetadata`. At minimum, document/require host applications to cross-check `request.shop` against a shop that is actually known/installed, and consider deriving a per-request signable string that combines body + shop + topic rather than relying on Shopify's own transport-level guarantees that headers cannot be forged, since this gem also accepts requests over an interface where those guarantees do not hold once the body/HMAC pair is replayed.

### Proof of Concept
1. Attacker installs the target app on their own dev shop `attacker.myshopify.com` and captures one legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`), see `lib/shopify_api/utils/hmac_validator.rb:26-31`.
2. Attacker sends a POST directly to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any `x-shopify-topic` they want.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers verbatim (`lib/shopify_api/webhooks/request.rb:45-63`), `Utils::HmacValidator.validate` succeeds because only `B` is checked (`lib/shopify_api/utils/hmac_validator.rb:12-22`), and `Registry.process` calls the registered handler with `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-199`) even though Shopify never sent anything on behalf of that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
