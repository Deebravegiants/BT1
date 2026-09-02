### Title
Webhook shop/topic identity spoofing due to HMAC covering only the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC verification performed by `Registry.process` binds none of the `shop-domain`, `topic`, `webhook-id`, or `api-version` values that the gem subsequently trusts and hands to the app's handler as the tenant/topic identity.

### Finding Description
The gem's HMAC check is: `Utils::HmacValidator.validate(request)` → `validate_signature` → `compute_signature(verifiable_query.to_signable_string, secret)` compared against the `hmac-sha256` header. [1](#0-0) 

For webhook requests, `to_signable_string` is defined to return `@raw_body` only: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers, not from the signed payload: [3](#0-2) 

`Registry.process` validates the HMAC (over body only), then uses `request.topic` to select the handler and forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` verbatim into `WebhookMetadata` given to the app's handler as the authoritative tenant/event identity: [4](#0-3) 

The equality the gem implicitly claims to guarantee is:
`hmac_valid(raw_body) == true` ⟺ `(shop, topic, webhook_id, api_version, raw_body)` all originated together from Shopify for that shop.

What is actually guaranteed is only:
`hmac_valid(raw_body) == true` ⟺ `raw_body` was produced by Shopify for *some* webhook delivery (to *some* shop, at *some* time, for *some* topic).

Because `shop`, `topic`, `webhook_id`, and `api_version` are not part of `to_signable_string`, any party who can send an HTTP request to the app's public webhook endpoint (this is a plain internet-facing route, e.g. `POST /callback/orders/create` per the documented Rails example) can attach a previously-observed valid `(raw_body, hmac)` pair — obtained from any legitimate webhook delivery, including one sent to their own store after installing the app themselves — together with **arbitrary** `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers of their choosing. `Utils::HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will happily dispatch the handler for the attacker-chosen topic with the attacker-chosen `shop` value in `WebhookMetadata`.

### Impact Explanation
This breaks the tenant-identity binding the whole webhook subsystem relies on. Host applications built on this gem are documented to trust `data.shop` from `WebhookMetadata` as the tenant to act on (the gem's own docs show `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), since the gem's job is precisely to "verify the request did indeed come from Shopify" before invoking the handler: [5](#0-4) [6](#0-5) 

A malicious merchant who installs the app on their own store legitimately receives real, correctly-signed webhooks (e.g., `orders/create` with body `B` and valid hmac `H`). They can then replay `(B, H)` to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop and/or the `shopify-topic`/`shopify-webhook-id` headers for a different, more sensitive topic (e.g. `shop/redact`, `app/uninstalled`, `customers/data_request`). The gem will report the HMAC as valid and hand the handler data claiming to be from the victim shop/topic, causing the host application to perform cross-tenant actions (e.g. writing attacker-controlled body content into the victim shop's records, triggering GDPR/redaction or uninstall side effects for a shop the attacker does not control) — this is cross-tenant access driven entirely by a gap in this gem's own verification logic, not by the host app ignoring documented behaviour, since the gem itself is what claims to have "verified the request did indeed come from Shopify."

### Likelihood Explanation
Likelihood is realistic for any app that is installable by third-party merchants (the common Shopify app distribution model): an attacker only needs to install the target app on a store they control to obtain one legitimately-signed `(raw_body, hmac)` pair, then can freely re-target it at any other tenant by rewriting unauthenticated headers on a direct HTTP POST to the app's public webhook route. No access token, `client_secret`, or privileged access is required — only the ability to install the app once and send crafted HTTP requests to its public endpoint.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the signed material checked by `to_signable_string`, or otherwise cryptographically bind them to the raw body before trusting them in `Registry.process`/`WebhookMetadata`, e.g. by making `to_signable_string` return a canonical concatenation of `shop-domain + topic + raw_body` (matching what the header values claim) so that `Utils::HmacValidator.validate` fails if any of these fields have been altered relative to what Shopify actually signed for that delivery.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`.
2. Capture a legitimate webhook delivery for topic `orders/create`: raw body `B`, header `shopify-hmac-sha256: H` (valid for `B` under the app's `client_secret`).
3. Send a direct HTTP POST to the app's public webhook endpoint (e.g. `POST /callback/orders/create`) with:
   - Body: `B`
   - Header `shopify-hmac-sha256: H` (unchanged, still valid since HMAC covers only `B`)
   - Header `shopify-shop-domain: victim-shop.myshopify.com` (attacker-chosen)
   - Header `shopify-topic: orders/create` (or any registered topic/mandatory topic)
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` is constructed by the host app exactly as documented.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which returns `true` because `to_signable_string` only checks `B` against `H`. [7](#0-6) 
6. The registered handler is invoked with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com`, even though this webhook never originated from Shopify for that shop, causing the host app to act on the victim tenant using attacker-supplied body content.

### Citations

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

**File:** docs/usage/webhooks.md (L24-26)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
