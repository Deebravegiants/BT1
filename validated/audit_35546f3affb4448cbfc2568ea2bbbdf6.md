## Title
Webhook shop-domain is not bound by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw request body only, excluding the `shop-domain` header. `HmacValidator.validate` therefore only proves that the *body* bytes were signed by the app's shared `api_secret_key` — it proves nothing about which shop the request claims to be from. Any actor who can generate one legitimately-signed webhook (i.e. a merchant who has installed the app on their own shop) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will dispatch it to the handler as if it came from the victim shop.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body — the `shop` accessor (sourced from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is never included in the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` verbatim when constructing the metadata handed to the app's handler: [3](#0-2) 

Because the app's `api_secret_key` is shared across *all* shops installing the app (it is not per-tenant), any merchant who legitimately installs the app can trigger a real webhook for their own shop, capture the resulting `(raw_body, hmac)` pair, and resend it to the same webhook endpoint with the `shop-domain` header changed to any other shop domain. `HmacValidator.validate` will still return `true` because it only checks that the body matches the HMAC — it never checks that the HMAC was computed for *that* shop. The equality the code should enforce, `hmac_signed(shop) == claimed(shop)`, is never checked; only `hmac_signed(body) == claimed(body)` is checked.

### Impact Explanation
This breaks tenant isolation for webhook processing: an attacker with access to a legitimately-installed shop can attribute arbitrary (attacker-controlled-body) webhook events to any other shop domain known to the app (shop domains are guessable/enumerable `*.myshopify.com` handles). Any host application logic that uses `webhook.shop` to key data updates, uninstall/GDPR handling, billing state, or app-state resets for a merchant would act on the wrong tenant, i.e. cross-tenant access/injection of forged events into another merchant's app data path.

### Likelihood Explanation
Requires only an internet-reachable webhook endpoint and one legitimate shop installation controlled by the attacker (a normal, unprivileged merchant account) — no access to the app's `client_secret`, no privileged account, and no interception of TLS is needed. The attacker only needs to observe their own valid webhook deliveries.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the signed/verified data, or independently bind the verified HMAC to the specific shop context expected for that webhook subscription (e.g., validate that `request.shop` matches the shop the subscription was registered for) rather than trusting the unauthenticated header value once body-HMAC validation succeeds.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets it trigger a real webhook (e.g. `orders/create`), capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker replays that exact body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which only checks `HMAC(secret, raw_body)` — this still matches, so validation passes.
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the app to process attacker-controlled data under the victim shop's identity. [4](#0-3) [5](#0-4)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
