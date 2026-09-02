This is the confirmed root cause: `ShopifyAPI::Webhooks::Request#hmac` binds only the raw request body via `to_signable_string` returning `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` come straight from HTTP headers and are never part of the signed content.### Title
Webhook HMAC only signs the request body, letting a replayed signature be paired with an arbitrary `shop-domain`/`topic` header to spoof cross-tenant webhooks - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking that the `x-shopify-hmac-sha256` header matches an HMAC of the raw request body. The tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) are read from separate, unsigned HTTP headers and are never included in the signed content. Any party who legitimately receives one valid `(body, hmac)` pair from Shopify (e.g., by installing the app on their own store) can replay that exact body+hmac to the app's webhook endpoint while freely rewriting the `shop-domain` and `topic` headers, causing the app to process attacker-chosen data under a victim shop's identity — an identity-binding break directly analogous to the `OmoRouter.transferFrom()` bug where an unverified `from` parameter let an attacker act on behalf of another party.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`hmac` is parsed from the `x-shopify-hmac-sha256`/`shopify-hmac-sha256` header, while `to_signable_string` returns only `@raw_body`. Crucially, `shop`, `topic`, `webhook_id`, and `api_version` are pulled from *other*, independent headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) that are **not** part of the signed string.

`Utils::HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, to_signable_string)` and compares it to the received `hmac`: [2](#0-1) 

`Registry.process` uses only this body-only check as its authentication gate, then immediately trusts the unsigned `request.shop` and `request.topic` to route and dispatch the webhook to the app's handler: [3](#0-2) 

The binding that is broken is:
`hmac_signed_bytes == raw_body` **but** `identity_used_for_dispatch (shop, topic) != hmac_signed_bytes`.

Because the shop/topic headers are excluded from the signature, a valid `(body, hmac)` pair generated for *any* shop (including one the attacker legitimately controls, such as their own development store where the same app is installed) can be replayed verbatim to the shared webhook endpoint with a forged `shop-domain` and/or `topic` header. `HmacValidator.validate` will still return `true` because it only re-derives the HMAC over the untouched body, and `Registry.process` will dispatch `WebhookMetadata.new(shop: request.shop, topic: request.topic, ...)` — attributing the (possibly attacker-influenced) payload to an arbitrary victim shop and/or arbitrary topic the attacker chooses, entirely bypassing the intended per-shop/per-topic authenticity guarantee webhook signature verification is supposed to provide.

### Impact Explanation
This crosses a tenant boundary without any privileged credential: the attacker never needs the app's `api_secret_key`, only a single legitimately-signed webhook body they were entitled to receive (trivial for any developer/merchant who installs the target app on their own store, or by observing any previously delivered webhook). By replaying that body under a spoofed `shop-domain` header, they can make the host application execute webhook-handling logic (e.g., data deletion for `shop/redact`, subscription/billing state changes, cache invalidation, order processing, etc.) attributed to a different, victim shop — a cross-tenant confusion/impersonation impact. Depending on how the host app's `WebhookHandler` uses `data.shop` (e.g., to look up and mutate that shop's stored session/data), this can lead to unauthorized cross-tenant data modification or deletion.

### Likelihood Explanation
High. No secret material is required — only the ability to receive one real webhook (any topic) from Shopify for a shop the attacker controls (installing the target public app is typically self-service), and knowledge of the shop's domain header format is public. This is a trivial replay attack against the gem's `Registry.process`/`Request`/`HmacValidator` implementation, reachable by any unprivileged internet user who can install the app once and then send a crafted HTTP POST with swapped headers to the webhook endpoint.

### Recommendation
Include the tenant-identifying and dispatch-relevant fields (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) inside the HMAC-signed content, not just the raw body, or otherwise cryptographically bind them (e.g., verify the signature over `headers + body`, or additionally require the app to separately validate `request.shop` against a known/installed-shop allow-list before trusting it for dispatch). At minimum, `Registry.process` should not treat `HmacValidator.validate(request)` as proof that `request.shop`/`request.topic` are authentic, since those fields are excluded from the signature.

```diff
File: lib/shopify_api/webhooks/request.rb

  sig { override.returns(String) }
  def to_signable_string
-   @raw_body
+   # bind shop/topic to the signed content so a valid (body, hmac) pair
+   # cannot be replayed under a different shop or topic
+   "#{shop}\n#{topic}\n#{@raw_body}"
  end
```
(Note: this specific diff is illustrative; the actual fix must match whatever canonicalization Shopify's servers use when computing the header HMAC, since `hmac-sha256` here is documented/tested as covering the body only. A safer fix is to require callers to enforce shop provenance out-of-band, e.g., only dispatch for `shop` values matching an app's own installed-shop store, rather than changing the signature scheme unilaterally.)

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (self-service, no privileged credential needed).
2. Shopify sends a legitimate webhook to the app's endpoint with headers:
   - `x-shopify-topic: orders/create`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of body B computed with the app's api_secret_key>`
   - body `B`
3. Attacker captures `(B, hmac)` (e.g., from their own server logs).
4. Attacker crafts a new HTTP POST to the same webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256` unchanged, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: shop/redact` (or any registered topic)
5. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate(request)` re-computes `HMAC(api_secret_key, B)`, which still matches the unchanged `hmac`, so validation passes ( [4](#0-3) ).
6. `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "shop/redact", body: parsed(B), ...)` ( [3](#0-2) ), causing the app to execute redact/other logic attributed to a shop the attacker does not control.

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
