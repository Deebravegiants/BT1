This confirms the vulnerability. The gem's documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  — but the HMAC validation only covers the raw body, not the shop-domain header, so this claim is only partially true (it verifies the app's secret signed *some* body, not which shop that body came from).

### Title
Webhook shop-domain spoofing via header/signature mismatch enables cross-tenant webhook injection - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb), [lib/shopify_api/webhooks/registry.rb](lib/shopify_api/webhooks/registry.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw request body [2](#0-1) . The `shop` value dispatched to the app's handler is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is **not** part of the signed content [3](#0-2) . This breaks the identity binding `shop-domain header == shop that produced this HMAC-signed body`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [4](#0-3) 

`HmacValidator.validate` / `validate_signature` compute and compare the HMAC over exactly that signable string using the app's `client_secret` (`Context.api_secret_key`): [5](#0-4) 

None of `topic`, `shop`, `api_version`, or `webhook_id` are included in the signed bytes — they are read straight from unauthenticated headers: [6](#0-5) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` when building `WebhookMetadata` passed to the app's handler, without any additional check that the shop belongs to the tenant that actually produced this signed body: [2](#0-1) 

Because all shops using the same app share the same `client_secret` (`Context.api_secret_key`) for webhook signing, an attacker who controls **any one shop** with the app installed (an unprivileged position obtainable by simply installing a free/dev app) can:
1. Trigger a real webhook from their own shop (e.g., `orders/create`) and capture the raw body + valid `x-shopify-hmac-sha256` value Shopify sent.
2. Replay that exact body + HMAC to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header (and optionally `topic`/`webhook-id`) to point at a **different, victim shop**.
3. `HmacValidator.validate` still succeeds because the signature only covers the body, which is unchanged; `Registry.process` calls the handler with `shop: request.shop` set to the victim's domain.

Any host application that uses `data.shop` from `WebhookMetadata` to look up per-shop state/sessions or to key subsequent Admin API calls (e.g. via `Session.temp(shop: data.shop, ...)`) will now act cross-tenant on behalf of a shop the attacker never controlled, using data the attacker fully authored (the replayed body) or with the attacker choosing an arbitrary topic/webhook-id.

This matches the report's manipulation pattern: an unprivileged party can force the system to accept attacker-chosen values (there: a fabricated derivative price via unconstrained trade prices; here: a fabricated shop identity via an HMAC scope that omits the field being trusted downstream) because the verification and the value that's acted upon are not the same bytes.

### Impact Explanation
This is a cross-tenant identity binding break: the gem hands the calling application a `shop` value that has no cryptographic tie to the signature it just validated. Any app that keys per-shop data, session lookups, or API actions off `WebhookMetadata#shop` (which is exactly the documented usage pattern shown in the gem's own docs, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be made to process attacker-controlled webhook bodies under a victim shop's identity — cross-tenant access.

### Likelihood Explanation
Requires only that the attacker be able to install the app on at least one shop (a normal, unprivileged action for any public/dev app) and be able to send an arbitrary HTTP POST with custom headers to the app's public webhook endpoint — no access token, secret, or privileged account is needed.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed content, or have `Registry.process`/`Request` cross-check the `shop` header against a shop-scoped secret/session rather than trusting the plain header value once the generic HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggers `orders/create`, and captures the POST: body `B`, header `x-shopify-hmac-sha256: H` (valid signature of `B` under the app's shared `client_secret`).
2. Attacker sends a new POST to the app's webhook route with the *same* body `B` and header `H`, but headers overridden as:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
3. `Utils::HmacValidator.validate` (via `HmacValidator#validate_signature`, `lib/shopify_api/utils/hmac_validator.rb:26-31`) computes `HMAC(secret, B)` and it matches `H`, so validation passes.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the registered handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, even though `victim-shop` never sent this webhook and its data never touched Shopify's signing for this request.

### Citations

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
