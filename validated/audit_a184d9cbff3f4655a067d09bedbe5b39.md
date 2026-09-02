### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, while the `shop` (and `topic`) values that are handed to the app's handler are taken from unauthenticated HTTP headers. Because the signing secret is the app-wide `api_secret_key` (identical for every shop that installs the app) rather than a per-shop secret, and because the signature never binds the `shop-domain` header, a request with a valid body/HMAC pair captured from one shop can be replayed with a different `x-shopify-shop-domain` header value and will still pass verification.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string using `Context.api_secret_key`: [2](#0-1) 

`Registry.process` only checks this body HMAC before dispatching to the handler, and constructs the metadata passed to the app's handler directly from unauthenticated headers (`request.shop`, `request.topic`, `request.webhook_id`): [3](#0-2) 

`request.shop` and `request.topic` are read straight from the `x-shopify-shop-domain` / `x-shopify-topic` headers with no cryptographic binding to the signed body: [4](#0-3) 

The broken identity binding, expressed as an equality that should hold but does not:
`shop_that_is_HMAC-covered == shop_used_by_handler_to_attribute_the_event`

Left side: nothing — no shop identifier participates in `to_signable_string`.
Right side: `request.shop`, taken verbatim from the `x-shopify-shop-domain` header.

Because `api_secret_key` is one shared value for the whole app (not scoped per-shop), any merchant who legitimately installs the app can capture one valid `(raw_body, hmac)` pair from a real webhook delivered to their own store, then replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header value naming a different, victim shop. `HmacValidator.validate` will still succeed because it never inspects the shop header, and `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: the library's only authentication mechanism for webhooks (body HMAC) provides no assurance about which shop an event belongs to. Any application logic that trusts `WebhookMetadata#shop` to select which merchant's session/access token/local record to act on (e.g., processing `orders/create`, `app/uninstalled`, GDPR mandatory topics, or updating per-shop local state) can be manipulated cross-tenant by a data-holder for one shop forging events "from" another shop. This matches the Critical "cross-tenant access" impact category, since it allows one tenant to inject/attribute events into another tenant's data path using only their own legitimate webhook traffic — no access token, refresh token, or leaked secret required.

### Likelihood Explanation
Likelihood is high for any app builder relying on the shipped `Registry`/`Request`/`WebhookMetadata` primitives as the sole authentication layer, since:
- The webhook endpoint is necessarily public/unauthenticated aside from this HMAC check.
- Any legitimate app installer already has the means to obtain one valid `(body, hmac)` pair merely by having the app installed on their own store and observing a webhook delivery.
- No additional secret or privileged credential is needed — only a standard webhook the attacker already legitimately receives for their own shop.
- The library provides no API or documentation instructing consumers to independently verify that the `shop` header corresponds to the source of the signed payload.

### Recommendation
Bind the shop identity (and topic) into the value that is cryptographically verified, e.g., by having `to_signable_string` incorporate the `shop-domain` (and `topic`) header alongside the body, or by requiring per-shop verification (compare `request.shop` against an independently known/authorized shop for that HMAC, such as a session lookup) before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a legitimate, permitted action).
2. Shopify delivers a real webhook, e.g. `orders/create`, to the app's endpoint with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of raw body computed with the app's api_secret_key>`
   - body: `{"id": 1, ...}`
3. Attacker captures this exact raw body and HMAC value (both are visible to them as the shop owner/inspecting their own network traffic).
4. Attacker replays an HTTP POST to the same public webhook endpoint with the identical body and HMAC header, but changes:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
5. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over the (unchanged) body using the same shared `api_secret_key` and it matches, so validation passes.
6. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: request.shop` → `"victim-shop.myshopify.com"`, and invokes the app's handler as if the event genuinely originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
