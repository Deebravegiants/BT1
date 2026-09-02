### Title
Webhook `shop-domain` and `topic` headers are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts the `shop` and `topic` values it hands to app-defined webhook handlers as if they were authenticated by the request's HMAC signature, but the HMAC computation only covers the raw body bytes. The `shop-domain` and `topic` headers used to build `WebhookMetadata` are read independently of the signature check, breaking the equality that should hold: `shop attributed to the event == shop authenticated by the HMAC`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, never the headers: [1](#0-0) 

`shop` and `topic` are read straight from (attacker-controllable) HTTP headers, with no cryptographic tie to the HMAC: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e. the body) against `verifiable_query.hmac`: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` uses this HMAC check as the sole gate, then dispatches to the handler keyed by `request.topic`, and constructs `WebhookMetadata` using `request.shop` — both values read from unauthenticated headers, not from anything verified by `Utils::HmacValidator.validate`: [4](#0-3) 

Because the body-HMAC is valid for *any* raw body that Shopify signed for *any* shop that has installed the app (an attacker can trivially obtain such a signed body/HMAC pair by triggering a webhook on their own store, since they control that tenant), an attacker who owns/controls one installed shop can take a legitimately-signed `(raw_body, hmac)` pair from their own tenant and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header pointing at a victim shop. `Utils::HmacValidator.validate` still returns `true` because it never inspects those headers, so `Registry.process` will invoke the app's handler believing the event legitimately originated from, and is scoped to, the victim shop.

### Impact Explanation
This breaks the tenant-isolation guarantee the library implicitly provides to host applications: "if `HmacValidator.validate` succeeds, the `shop` and `topic` fields on the resulting `WebhookMetadata` can be trusted as authenticated by Shopify for that shop." In reality only the body bytes are authenticated. A host application that (reasonably, given the API surface) uses `WebhookMetadata#shop` to select which tenant's data to mutate (e.g. store an order, process a GDPR redact/uninstall event, update per-shop settings) can be made to attribute attacker-controlled event data to an arbitrary victim tenant — a cross-tenant boundary violation reachable by any unprivileged user who can install the app on their own store (a normal, unprivileged action).

### Likelihood Explanation
Likelihood is moderate-to-high for apps that install on the public app store: any user can install the target app on a store they control, trigger arbitrary webhook topics they subscribed to (e.g. by creating orders, updating products, etc.), capture the resulting `(raw_body, X-Shopify-Hmac-Sha256)` pair (available at the attacker's own webhook receiver or by intercepting/logging it), and replay it against the app's public webhook endpoint with modified `shop`/`topic` headers. No knowledge of `api_secret_key` or any credential is required — the attacker leverages a signature Shopify already produced for them.

### Recommendation
Include the shop domain (and ideally the topic and API version) in the value that is HMAC-verified, or otherwise cryptographically/contextually bind them — e.g., require the caller to supply the expected shop and compare it against a value verified out-of-band (mTLS/IP allow-list from Shopify, or a per-shop webhook secret), and have `Registry.process` reject processing if the header-derived `shop`/`topic` cannot be shown to correspond to the same request Shopify actually signed. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are **not** covered by the HMAC check and must not be trusted for tenant-scoping decisions without additional verification (e.g., cross-checking against a shop that is already known/registered for that specific HMAC/body combination via delivery logs), and consider incorporating the headers into the signable string if Shopify's delivery contract allows it.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged action for any Shopify user) and configures/observes a webhook subscription (e.g. `products/update`).
2. Attacker triggers the event on their own store; Shopify delivers a POST to the app's webhook endpoint with headers:
   - `X-Shopify-Topic: products/update`
   - `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body using the app's shared secret>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - body: `raw_body`
3. Attacker captures `raw_body` and the `X-Shopify-Hmac-Sha256` value (trivial, since it was delivered to infrastructure they control).
4. Attacker sends a new POST directly to the app's public webhook endpoint with the same `raw_body` and same `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic` that is also registered).
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only `raw_body` is checked: [5](#0-4) 
6. The handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the event actually originated from the attacker's own store, achieving cross-tenant event/data spoofing.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
