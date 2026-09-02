## Title
Webhook `Request#to_signable_string` signs only the raw body, so `HmacValidator.validate` authenticates content that is never bound to the shop/topic used downstream - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`HmacValidator.validate` is the sole authenticity check for both OAuth callbacks and webhooks, but what it verifies differs by artefact type. For `Auth::Oauth::AuthQuery`, the signed string embeds `shop`, `code`, `host`, `state`, `timestamp`, so the value verified is the same value later acted on - no divergence there. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`; the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers used by `Registry.process` are never part of the signed material.

## Finding Description
The claimed invariant is: **shop authenticated by the signature == shop used downstream**.

- OAuth path: `AuthQuery#to_signable_string` (`lib/shopify_api/auth/oauth/auth_query.rb:34-43`) builds the signable string from `code, host, shop, state, timestamp`. `Oauth.validate_auth_callback` (`lib/shopify_api/auth/oauth.rb:64,73,97`) only ever uses `auth_query.shop` / `auth_query.code`, both of which are literally inside the signed string. Equality holds; no divergence here. [1](#0-0) [2](#0-1) 

- Webhook path: `Webhooks::Request#to_signable_string` returns `@raw_body` only, and `shop`, `topic`, `webhook_id`, `api_version` are read straight from HTTP headers, not included in the HMAC input. [3](#0-2) 

`Registry.process` calls `Utils::HmacValidator.validate(request)` and, on success, dispatches using `request.topic` and constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` - i.e. it treats `topic` and `shop` as authenticated because they came from a "validated" request object, when in fact only the raw body bytes were checked against the HMAC. [4](#0-3) 

`HmacValidator.validate`/`validate_signature` only compares `compute_signature(verifiable_query.to_signable_string, secret)` against `verifiable_query.hmac`; it has no knowledge of, and cannot bind, any header value that isn't included in `to_signable_string`. [5](#0-4) 

Exploit flow: an attacker installs the app on their own shop (unprivileged, permitted by the rules) and receives genuine webhooks from Shopify — e.g. body `B` with a correct `X-Shopify-Hmac-Sha256` signature computed over `B` using the shared `api_secret_key`. Because the signature covers only `B`, the attacker can replay `B` + the same HMAC to the app's own webhook endpoint directly (bypassing Shopify) while forging the `X-Shopify-Shop-Domain` and/or `X-Shopify-Topic` headers to name a victim shop or a different topic (e.g. a mandatory `shop/redact` topic, or `app/uninstalled`). `HmacValidator.validate` still returns `true` because the body/HMAC pair is unchanged, and `Registry.process` proceeds to call the topic's handler with `shop: request.shop` set to the attacker's forged value.

## Impact Explanation
This lets an attacker who legitimately installed the app on one shop make the app process a "validated" webhook attributed to an arbitrary victim shop and/or arbitrary topic, since neither `shop` nor `topic` is bound by the signature. Depending on what host-app webhook handlers do with `WebhookMetadata#shop`/`#topic` (e.g. looking up/deleting sessions, triggering data-deletion flows, or performing shop-scoped API actions), this is a cross-tenant authentication-bypass class issue: a forged webhook (wrong topic/shop attribution) is accepted as authentic by the gem's own arbitrator. It is repeatable against any victim shop name the attacker chooses to put in the header, for as many webhook bodies as the attacker can legitimately obtain from their own installation.

## Likelihood Explanation
Preconditions are minimal and match the stated threat model exactly: the attacker only needs to install the app on their own development shop (no special privileges), capture one authentic webhook body+HMAC pair, and send a single crafted HTTP POST directly to the app's public webhook endpoint with forged Shopify headers. No secret, token, or victim interaction is required. Cost is a single self-installed app plus one HTTP request; it is trivially repeatable.

## Recommendation
Include the `shop-domain`, `topic`, and `webhook-id` header values in `Webhooks::Request#to_signable_string` (or otherwise cryptographically bind them, e.g. by validating them against a value obtained through the authenticated session/API rather than the raw header), so `HmacValidator.validate` can no longer return `true` for a signed body attached to attacker-chosen header metadata.

## Proof of Concept
```ruby
# test/webhooks/request_binding_test.rb (proposed)
require_relative "../test_helper"

class WebhookShopBindingTest < Test::Unit::TestCase
  def test_hmac_does_not_bind_shop_or_topic_header
    body = '{"id":1}'
    secret = ShopifyAPI::Context.api_secret_key
    valid_hmac = Base64.encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, body)
    ).strip

    # Attacker's own shop originally received this signed body for topic "orders/create"
    original = ShopifyAPI::Webhooks::Request.new(
      raw_body: body,
      headers: {
        "x-shopify-topic" => "orders/create",
        "x-shopify-hmac-sha256" => valid_hmac,
        "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
      },
    )
    assert(ShopifyAPI::Utils::HmacValidator.validate(original))

    # Same body/hmac replayed with forged shop + topic headers
    forged = ShopifyAPI::Webhooks::Request.new(
      raw_body: body,
      headers: {
        "x-shopify-topic" => "shop/redact",
        "x-shopify-hmac-sha256" => valid_hmac,
        "x-shopify-shop-domain" => "victim-shop.myshopify.com",
      },
    )

    # Both sides of the "shop binding" equality diverge (attacker-shop vs victim-shop,
    # orders/create vs shop/redact) yet validate() still returns true.
    assert(ShopifyAPI::Utils::HmacValidator.validate(forged))
    assert_equal("victim-shop.myshopify.com", forged.shop)
    assert_equal("shop/redact", forged.topic)
  end
end
```
This demonstrates that `HmacValidator.validate` returns `true` regardless of the (forged) `shop`/`topic` headers, proving the signature never authenticated the values `Registry.process` subsequently trusts and acts upon.

### Citations

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** lib/shopify_api/auth/oauth.rb (L60-98)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state

          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
          response = begin
            client.request(
              Clients::HttpRequest.new(
                http_method: :post,
                path: "access_token",
                body: body,
                body_type: "application/json",
              ),
            )
          rescue ShopifyAPI::Errors::HttpResponseError => e
            raise Errors::RequestAccessTokenError,
              "Cannot complete OAuth process. Received a #{e.code} error while requesting access token."
          end

          session_params = T.cast(response.body, T::Hash[String, T.untyped]).to_h
          session = Session.from(shop: auth_query.shop,
            access_token_response: Oauth::AccessTokenResponse.from_hash(session_params))
```

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
