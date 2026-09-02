### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw request body, while the `shop` (and `topic`/`webhook-id`) values that identify *which tenant* the webhook belongs to are read directly from unauthenticated HTTP headers. `Registry.process` validates the body's HMAC and then hands the header-derived, unverified `shop` value straight to the app's webhook handler as the tenant identity. This breaks the same identity-binding invariant flagged in the external report: a field that is *acted upon* (`shop`, used to attribute/authorize the webhook to a tenant) is not *covered by* the authentication mechanism (`HMAC`) that is supposed to prove authenticity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the body's HMAC via `Utils::HmacValidator.validate`, then immediately forwards the unauthenticated `request.shop` (along with `topic`, `api_version`, `webhook_id`) into `WebhookMetadata` and into the app's registered handler: [3](#0-2) 

`HmacValidator.validate_signature` compares only the computed HMAC of the signable string (the body) against the received HMAC using the app's single, shop-agnostic `api_secret_key`: [4](#0-3) 

Because the same `api_secret_key` is used to sign every shop's webhooks for a given app, and the signature never covers `shop-domain`, any two webhook deliveries whose bodies are identical (or where the body doesn't itself carry a shop identifier that the handler cross-checks) produce interchangeable, header-swappable payloads: a payload legitimately signed for shop A's webhook can be replayed with the `X-Shopify-Shop-Domain` header rewritten to shop B, and the signature will still validate, because it is only a function of the body bytes and the app secret — not of which shop sent it.

The equality this breaks: **the tenant identity acted upon (`request.shop`, passed to the handler as `WebhookMetadata#shop`) must equal the tenant whose bytes were actually verified by the HMAC** — but the HMAC only verifies `@raw_body`, never `shop`.

### Impact Explanation
If a host application relies on the `shop` value provided by `WebhookMetadata` (as the library's own documentation instructs apps to do) to determine which tenant's data/session to act on — e.g., "look up shop A's session and mutate shop A's local records based on this webhook" — an attacker who controls one installed shop can capture a validly-HMAC'd webhook body from their own shop and resubmit it directly to the app's webhook endpoint with a forged `shop-domain` header pointing at a victim shop. Since the gem never binds `shop` to the signature, the forged request passes `Registry.process`'s HMAC check and is dispatched to the handler labeled with the victim's shop, resulting in cross-tenant data confusion/write (Critical: cross-tenant access) if the handler's logic is keyed off of `data.shop` for record identification or session lookup, which is precisely the pattern the library encourages via `WebhookMetadata`.

### Likelihood Explanation
The attacker needs only an existing (even free/no-cost) install of the target app on their own shop to legitimately receive a real, correctly-signed webhook, and the ability to send arbitrary HTTP requests directly to the app's public webhook endpoint (bypassing Shopify's delivery infrastructure entirely, which the gem does nothing to prevent since it does not restrict caller IPs or require any header binding). No access to `api_secret_key`, tokens, or victim credentials is needed. This requires the specific condition that the webhook `topic`'s body content is shop-independent or attacker-influenceable in a way useful to the attacker (e.g., topics whose payload alone doesn't disambiguate a shop, or where the attacker crafts their own shop's data to match a target's expected format), making exploitability topic-dependent but structurally always possible given the missing binding.

### Recommendation
Include the shop-identifying and topic-identifying headers in the HMAC-signable string, or otherwise cryptographically bind them (e.g., derive an expected value and enforce equality against a value stored server-side, or require verification callers to pass the expected shop and let the library assert equality). At minimum, extend `Request#to_signable_string` to canonicalize and include `shop`, `topic`, and `webhook_id` alongside the raw body so `HmacValidator.validate` covers the full attributed identity, not merely the payload bytes:
```ruby
def to_signable_string
  "#{shop}|#{topic}|#{webhook_id}|#{@raw_body}"
end
```
(with a corresponding, coordinated change needed on the verification side to match Shopify's actual signing scheme, since Shopify's own HMAC computation would also need to include these fields for this to work without breaking legitimate deliveries — this may require Shopify platform-side changes rather than being fully fixable client-side).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook topic whose body content they can predict/control (e.g., `app/uninstalled`, or any topic with an empty/templated body) and captures the legitimate request, including a valid `X-Shopify-Hmac-Sha256` header computed by Shopify over that body using the app's `api_secret_key`.
3. Attacker replays the exact same raw body and valid HMAC header to the app's public webhook endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `@raw_body` against the HMAC [5](#0-4) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the request never actually originated from Shopify on behalf of that shop [6](#0-5) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
