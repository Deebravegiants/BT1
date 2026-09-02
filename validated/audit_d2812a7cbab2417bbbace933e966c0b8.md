This confirms the vulnerability. Let me verify the `topic` header is also used to dispatch to a specific registered handler (which may deserialize/process the body differently), reinforcing the impact.### Title
Webhook `shop-domain` and `topic` headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never included in the signed material. `Webhooks::Registry.process` validates only the body-derived HMAC and then unconditionally trusts the header-derived `shop` and `topic` to route the payload and attribute it to a tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled from headers that are outside that signed string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)` (which hashes `to_signable_string`, i.e. the body only), then immediately trusts `request.shop` and `request.topic` to select the handler and build the metadata passed to app code: [3](#0-2) 

The binding the app relies on is: *shop authenticated (HMAC-covered) == shop the handler processes data as*. Here, only the body is HMAC-covered; the `shop` (and `topic`) the handler actually uses come from unauthenticated headers. Any caller who can produce one valid `(raw_body, hmac)` pair — trivially available since a merchant/attacker who installs the app on their own store will receive genuine webhooks with a valid HMAC computed with the app's `api_secret_key` over their own body — can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) with an arbitrary victim shop domain or topic. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` dispatches the attacker-chosen body content to the handler tagged as coming from the victim shop: [4](#0-3) 

This never requires knowledge of `api_secret_key` beyond what the attacker already legitimately possesses via their own installed instance of the app — no privileged secret or token theft is needed.

### Impact Explanation
This breaks tenant isolation for any application that keys persisted data, cache invalidation, deprovisioning, or authorization decisions off `WebhookMetadata#shop`/`#topic` without independently verifying header authenticity (which the gem does nothing to encourage/enable, since it doesn't expose header-bound HMAC verification). An attacker can inject/spoof events attributed to a shop they don't own — e.g., trigger `shop/redact` or `app/uninstalled`-style handling, corrupt another tenant's cached data, or force business logic keyed by `shop` to run against a victim's records — constituting cross-tenant access/data corruption, matching the Critical impact class ("cross-tenant access").

### Likelihood Explanation
Any developer/attacker can install the target app on a shop they control to legitimately receive a validly HMAC-signed webhook body from Shopify, then replay that same body+HMAC to the app's public webhook endpoint with a forged `shop-domain` (and/or `topic`) header. No access to `api_secret_key`, tokens, or privileged accounts is required — only the ability to send an HTTP POST to the app's publicly reachable webhook route, which is inherent to how webhook endpoints work.

### Recommendation
Include `shop`, `topic`, and any other header fields the handler acts on inside the signed material that is verified, or independently bind/verify these header values (e.g., cross-check `shop-domain` against a value looked up via the `webhook_id`/API call, or require the caller to additionally validate shop identity through a side channel) before invoking the handler. At minimum, document and enforce that `Registry.process` must reject or re-verify shop/topic headers rather than trusting them implicitly once body HMAC passes.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`; trigger any subscribed webhook topic so Shopify delivers a request with a real `x-shopify-hmac-sha256` computed over some `raw_body` using the app's `api_secret_key`.
2. Capture that `(raw_body, x-shopify-hmac-sha256)` pair.
3. Replay a POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`).
4. `Utils::HmacValidator.validate(request)` returns `true` (body untouched), `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` sourced purely from the unauthenticated header, causing the app to process attacker-supplied data as if it originated from the victim shop.

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
